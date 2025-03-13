from pathlib import Path
from enum import Enum, unique
from dataclasses import dataclass
from git import Repo, GitCommandError
from dotctl.paths import app_profile_directory
import logging

# Configure logging for better debugging
logging.basicConfig(level=logging.ERROR)


@dataclass
class ListerProps:
    profile_dir: Path
    details: bool


lister_default_props = ListerProps(
    Path(app_profile_directory),
    details=False,
)


@dataclass
class ProfileManagerProps:
    title: str
    icon: str
    desc: str


@dataclass
class ProfileActiveProps:
    is_active: bool
    icon: str


@dataclass
class ProfileStatusProps:
    title: str
    icon: str
    desc: str


@unique
class ProfileActiveStatus(Enum):
    active = ProfileActiveProps(
        is_active=True,
        icon="🟢",
    )
    not_active = ProfileActiveProps(
        is_active=False,
        icon="➖",
    )


@unique
class ProfileManager(Enum):
    local = ProfileManagerProps(
        title="Local",
        icon="🏠",
        desc="Profile Managed Locally",
    )
    remote = ProfileManagerProps(
        title="Remote",
        icon="🌐",
        desc="Profile Managed Remotely",
    )


@unique
class ProfileStatus(Enum):
    local = ProfileStatusProps(
        title="Local",
        icon="🏠",
        desc="Profile Managed Locally",
    )
    remote = ProfileStatusProps(
        title="Remote",
        icon="🌐",
        desc="Profile Managed Remotely",
    )
    synced = ProfileStatusProps(
        icon="✅",
        title="Synced",
        desc="Profile Synced with Cloud",
    )
    stale_remote = ProfileStatusProps(
        icon="📦",
        title="Archived",
        desc="Previously available profile, may be outdated",
    )
    behind_remote = ProfileStatusProps(
        icon="⬇️",
        title="Update Available",
        desc="Newer version of this profile is available on cloud",
    )
    ahead_remote = ProfileStatusProps(
        icon="⬆️",
        title="Locally Updated",
        desc="This profile has local updates not yet synced",
    )


@dataclass
class Profile:
    name: str
    status: ProfileStatus
    active_status: ProfileActiveStatus


def determine_profile_status(
    repo: Repo, branch: str, local_branches: set, remote_branches: set
) -> ProfileStatus:
    try:
        if branch in local_branches and branch in remote_branches:
            ahead = int(repo.git.rev_list(f"origin/{branch}..{branch}", count=True))
            behind = int(repo.git.rev_list(f"{branch}..origin/{branch}", count=True))

            if ahead > 0:
                return ProfileStatus.ahead_remote
            elif behind > 0:
                return ProfileStatus.behind_remote
            else:
                return ProfileStatus.synced  # Fully Synced
        elif branch in remote_branches:
            return ProfileStatus.remote  # Remote-only profile
        elif branch in local_branches:
            repo.git.rev_list(f"origin/{branch}")  # Check if remote exists
            return ProfileStatus.local
    except GitCommandError:
        # logging.error(f"Error checking status of branch: {branch}")
        return ProfileStatus.local  # More cautious fallback
    return ProfileStatus.local


def get_profile_list(props: ListerProps):
    try:
        repo = Repo(props.profile_dir)

        if repo.bare:
            print("The repository is bare. No branches available.")
            return

        active_branch = repo.active_branch.name
        local_branches = {branch.name for branch in repo.branches}

        try:
            remote_branches = {
                ref.name.replace("origin/", "")
                for ref in repo.remotes.origin.refs
                if ref.name != "origin/HEAD"
            }
        except GitCommandError:
            remote_branches = set()

        all_branches = local_branches | remote_branches | {active_branch}

        branch_list = [
            f"{active_status.value.icon} {branch} {profile_status.value.icon}"
            + (
                f": ({profile_status.value.title}) - {profile_status.value.desc}"
                if props.details
                else ""
            )
            for branch in all_branches
            for active_status in [
                (
                    ProfileActiveStatus.active
                    if branch == active_branch
                    else ProfileActiveStatus.not_active
                )
            ]
            for profile_status in [
                determine_profile_status(repo, branch, local_branches, remote_branches)
            ]
        ]

        print("\n".join(branch_list))

    except GitCommandError as e:
        logging.error(f"Git command error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
