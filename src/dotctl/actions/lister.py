import sys
from pathlib import Path
from enum import Enum, unique
from dataclasses import dataclass
import getpass
from git import Repo, GitCommandError, InvalidGitRepositoryError
from dotctl.paths import app_profile_directory
from dotctl.utils import log
from dotctl.exception import exception_handler
from dotctl import __APP_NAME__


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


@dataclass
class ProfileMetaData:
    repo_name: str
    owner: str
    last_commit_author: str


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
def get_profile_meta(profile_dir: Path = Path(app_profile_directory)):
    repo = Repo(profile_dir)

    if repo.bare:
        return ProfileMetaData(
            repo_name=profile_dir.name,
            owner=getpass.getuser(),
            last_commit_author="No commits",
        )

    remote_url = repo.remotes.origin.url if repo.remotes else "No remote"

    try:
        last_commit = repo.head.commit
        last_commit_author = last_commit.author.name or "Unknown"
    except ValueError:  # Handles empty repos (no commits yet)
        last_commit_author = "No commits"

    if remote_url != "No remote":
        if remote_url.startswith("git@"):
            repo_name = remote_url.split(":")[-1].replace(".git", "")
            owner = remote_url.split(":")[-1].split("/")[0]
        else:
            repo_name = remote_url.split("/")[-1].replace(".git", "")
            owner = remote_url.split("/")[-2]
    else:
        repo_name = profile_dir.name
        owner = (
            last_commit_author
            if last_commit_author != "No commits"
            else getpass.getuser()
        )

    return ProfileMetaData(
        repo_name=repo_name,
        owner=owner,
        last_commit_author=last_commit_author,
    )


@exception_handler
def get_profile_list(props: ListerProps):
    if not props.profile_dir.exists():
        log(f"Profile repo not yet initialized, run `{__APP_NAME__} init` first.")
        sys.exit(1)

    try:
        repo = Repo(props.profile_dir)

        if repo.bare:
            print("The repository is bare. No profiles available.")
            return

        if props.fetch:
            try:
                if repo.remotes:
                    origin = next(
                        (remote for remote in repo.remotes if remote.name == "origin"),
                        None,
                    )
                    if origin:
                        origin.fetch(prune=True)
            except GitCommandError as e:
                log(f"Failed to fetch remote: {e}")

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
            profile_meta = get_profile_meta()
            print("-" * 40)
            print(f"Repository: {profile_meta.repo_name}")
            print(f"Owner: {profile_meta.owner}")
            print(f"Last Commit Author: {profile_meta.last_commit_author}")

    except GitCommandError as e:
        log(f"Git command error: {e}")
    except InvalidGitRepositoryError as e:
        log(f"Profile repo not yet initialized, run `{__APP_NAME__} init` first.")
    except Exception as e:
        raise Exception(f"Unexpected error: {e}")
