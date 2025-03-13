from pathlib import Path
from enum import Enum
from dataclasses import dataclass
from git import Repo, GitCommandError
from tabulate import tabulate
from dotctl.paths import app_profile_directory


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


class ProfileActiveStatus(Enum):
    active = ProfileActiveProps(
        is_active=True,
        icon="🟢",
    )
    not_active = ProfileActiveProps(
        is_active=False,
        icon="➖",
    )


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


class ProfileStatus(Enum):
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
    # manager: ProfileManager
    status: ProfileStatus
    active_status: ProfileActiveStatus


def determine_profile_status(
    repo: Repo, branch: str, local_branches: set, remote_branches: set
) -> ProfileStatus:
    if branch in local_branches and branch in remote_branches:
        # Check if the branch is ahead or behind the remote
        try:
            ahead = int(repo.git.rev_list(f"origin/{branch}..{branch}", count=True))
            behind = int(repo.git.rev_list(f"{branch}..origin/{branch}", count=True))

            if ahead > 0:
                return ProfileStatus.ahead_remote
            elif behind > 0:
                return ProfileStatus.behind_remote
            else:
                return ProfileStatus.synced  # Fully Synced
        except GitCommandError:
            return ProfileStatus.synced  # Assume synced if error occurs
    elif branch in remote_branches:
        return ProfileStatus.remote  # Remote-only profile
    elif branch in local_branches:
        try:
            repo.git.rev_list(f"origin/{branch}")
        except GitCommandError:
            return (
                ProfileStatus.stale_remote
            )  # Remote branch deleted, local copy exists
        return ProfileStatus.local
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

        branch_list = []
        all_branches = local_branches | remote_branches | {active_branch}

        for branch in all_branches:
            active_status = (
                ProfileActiveStatus.active
                if branch == active_branch
                else ProfileActiveStatus.not_active
            )

            profile_status = determine_profile_status(
                repo, branch, local_branches, remote_branches
            )

            profile = Profile(
                active_status=active_status,
                name=branch,
                status=profile_status,
            )
            is_active = active_status.value.icon
            icon = profile.status.value.icon
            title = profile.status.value.title
            desc = profile.status.value.desc

            profile_str = f"{is_active} {branch} {icon}"
            if props.details:
                profile_str += f": ({title}) - {desc}"

            branch_list.append(profile_str)

        print("\n".join(branch_list))

    except GitCommandError as e:
        print(f"Git command error: {e}")
    except Exception as e:
        print(f"Error: {e}")
