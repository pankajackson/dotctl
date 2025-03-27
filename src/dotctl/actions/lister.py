from pathlib import Path
from enum import Enum, unique
from dataclasses import dataclass
from git import Repo, GitCommandError, InvalidGitRepositoryError
from dotctl.paths import app_profile_directory
from dotctl.utils import log
from dotctl.exception import exception_handler
from dotctl.handlers.git_handler import (
    get_repo,
    get_repo_branches,
    git_fetch,
    get_repo_meta,
)


@dataclass
class ListerProps:
    profile_dir: Path
    details: bool
    fetch: bool


lister_default_props = ListerProps(
    Path(app_profile_directory),
    details=False,
    fetch=False,
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
                return ProfileStatus.synced
        elif profile in remote_profiles:
            return ProfileStatus.remote
        elif profile in local_profiles:
            if repo.remotes:
                return ProfileStatus.stale_remote
            else:
                return ProfileStatus.local
    except GitCommandError:
        return ProfileStatus.local
    return ProfileStatus.local


@exception_handler
def get_profile_list(props: ListerProps):
    log("Fetching profiles...")
    repo = get_repo(props.profile_dir)

    try:
        if repo.bare:
            print("The repository is bare. No profiles available.")
            return

        if props.fetch:
            git_fetch(repo)

        local_profiles, remote_profiles, active_profile, all_profiles = (
            get_repo_branches(repo)
        )

        profile_list = [
            Profile(
                name=profile,
                status=determine_profile_status(
                    repo=repo,
                    profile=profile,
                    local_profiles=local_profiles,
                    remote_profiles=remote_profiles,
                ),
                active_status=(
                    ProfileActiveStatus.active
                    if profile == active_profile
                    else ProfileActiveStatus.not_active
                ),
            )
            for profile in sorted(all_profiles)
        ]

        profile_list_string = " \n".join(
            [
                (
                    f"  {profile.active_status.value.icon} {profile.name} {profile.status.value.icon}"
                    if not props.details
                    else f"  {profile.active_status.value.icon} {profile.name} {profile.status.value.icon} ({profile.status.value.title}) - {profile.status.value.desc}"
                )
                for profile in profile_list
            ]
        )
        print(f"Profiles:\n{profile_list_string}")
        if props.details:
            profile_meta = get_repo_meta(repo=repo)
            print("-" * 50)
            print(f"Repository: {profile_meta.repo_name}")
            print(f"Owner: {profile_meta.owner}")
            print(f"Last Commit Author: {profile_meta.last_commit_author}")

    except Exception as e:
        raise Exception(f"Unexpected error: {e}")
