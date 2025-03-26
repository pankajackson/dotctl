import sys
from pathlib import Path
from dataclasses import dataclass
import getpass
from git import Repo, GitCommandError, InvalidGitRepositoryError
from dotctl.paths import app_profile_directory
from dotctl.utils import log
from dotctl.exception import exception_handler
from dotctl.handlers.git_handler import (
    get_repo,
    get_repo_branches,
    git_fetch,
    checkout_branch,
)
from dotctl import __APP_NAME__, __DEFAULT_PROFILE__


@dataclass
class SwitcherProps:
    profile: str | None
    profile_dir: Path
    fetch: bool


switcher_default_props = SwitcherProps(
    profile=None,
    profile_dir=Path(app_profile_directory),
    fetch=False,
)


@exception_handler
def switch(props: SwitcherProps):
    repo = get_repo(props.profile_dir)

    if repo.bare:
        log("The repository is bare. No Profile available.")
        sys.exit(1)

    local_profiles, remote_profiles, active_profile, all_profiles = get_repo_branches(
        repo
    )

    # Determine the profile (branch) to switch to
    if props.profile:
        profile_name = props.profile
    else:
        profile_name = (
            repo.git.symbolic_ref("refs/remotes/origin/HEAD").split("/")[-1]
            if repo.remotes and "origin" in repo.remotes
            else __DEFAULT_PROFILE__
        )

    if profile_name == active_profile:
        log(f"Already on the current profile: {profile_name}")
        return

    # Fetch remote branches if requested
    if props.fetch:
        git_fetch(repo)

    if profile_name not in all_profiles:
        git_fetch(repo)
    if profile_name in local_profiles:
        # Checkout local branch
        checkout_branch(repo, profile_name)
        log(f"Switched to profile: {profile_name}")
    elif profile_name in remote_profiles:
        # Checkout and track remote branch automatically
        checkout_branch(repo, profile_name)
        log(f"Downloaded and switched to new profile from cloud: {profile_name}")
    else:
        log(f"Profile '{profile_name}' is not available in the repository.")
