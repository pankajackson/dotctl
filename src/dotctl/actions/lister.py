from pathlib import Path
from enum import Enum, unique
from dataclasses import dataclass
from git import Repo, GitCommandError
from dotctl.paths import app_profile_directory
from dotctl.utils import log
from dotctl.exception import exception_handler


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


@exception_handler
def determine_profile_status(
    repo: Repo, profile: str, local_profiles: set, remote_profiles: set
) -> ProfileStatus:
    try:
        if profile in local_profiles and profile in remote_profiles:
            ahead = int(repo.git.rev_list(f"origin/{profile}..{profile}", count=True))
            behind = int(repo.git.rev_list(f"{profile}..origin/{profile}", count=True))

            if ahead > 0:
                return ProfileStatus.ahead_remote
            elif behind > 0:
                return ProfileStatus.behind_remote
            else:
                return ProfileStatus.synced  # Fully Synced
        elif profile in remote_profiles:
            return ProfileStatus.remote  # Remote-only profile
        elif profile in local_profiles:
            repo.git.rev_list(f"origin/{profile}")  # Check if remote exists
            return ProfileStatus.local
    except GitCommandError:
        return ProfileStatus.local  # More cautious fallback
    return ProfileStatus.local


@exception_handler
def get_profile_list(props: ListerProps):
    try:
        repo = Repo(props.profile_dir)

        if repo.bare:
            print("The repository is bare. No profiles available.")
            return

        active_profile = repo.active_branch.name
        local_profiles = {profile.name for profile in repo.branches}

        try:
            remote_profiles = set()
            if repo.remotes:
                try:
                    origin = next(
                        (remote for remote in repo.remotes if remote.name == "origin"),
                        None,
                    )
                    if origin:
                        remote_profiles = {
                            ref.name.replace("origin/", "")
                            for ref in origin.refs
                            if ref.name != "origin/HEAD"
                        }
                except GitCommandError:
                    remote_profiles = set()
        except GitCommandError:
            remote_profiles = set()

        all_profiles = local_profiles | remote_profiles | {active_profile}

        profile_list = [
            f"{active_status.value.icon} {profile} {profile_status.value.icon}"
            + (
                f": ({profile_status.value.title}) - {profile_status.value.desc}"
                if props.details
                else ""
            )
            for profile in all_profiles
            for active_status in [
                (
                    ProfileActiveStatus.active
                    if profile == active_profile
                    else ProfileActiveStatus.not_active
                )
            ]
            for profile_status in [
                determine_profile_status(repo, profile, local_profiles, remote_profiles)
            ]
        ]

        print("\n".join(profile_list))

    except GitCommandError as e:
        log(f"Git command error: {e}")
    except Exception as e:
        log(f"Unexpected error: {e}")
