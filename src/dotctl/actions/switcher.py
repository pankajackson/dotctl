import sys
from pathlib import Path
from dataclasses import dataclass
import getpass
from git import Repo, GitCommandError, InvalidGitRepositoryError
from dotctl.paths import app_profile_directory
from dotctl.utils import log
from dotctl.exception import exception_handler
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
    """
    Switches to the given branch (profile) if it exists in the local or remote repository.
    If the profile is None, it switches to the default branch.
    """

    try:
        repo = Repo(props.profile_dir)
    except InvalidGitRepositoryError:
        log(f"Profile repo not yet initialized, run `{__APP_NAME__} init` first.")
        sys.exit(1)

    if repo.bare:
        log("The repository is bare. No Profile available.")
        sys.exit(1)

    # Check if the repo has any commits
    has_commits = repo.head.is_valid() if repo.head else False

    # Determine the profile (branch) to switch to
    if props.profile:
        profile_name = props.profile
    else:
        profile_name = (
            repo.git.symbolic_ref("refs/remotes/origin/HEAD").split("/")[-1]
            if repo.remotes and "origin" in repo.remotes
            else __DEFAULT_PROFILE__
        )

    try:
        current_branch = repo.active_branch.name
    except TypeError:
        current_branch = None  # Handles detached HEAD state or uninitialized repo

    if profile_name == current_branch:
        log(f"Already on the current profile: {profile_name}")
        return

    # Fetch remote branches if requested
    if props.fetch and repo.remotes:
        try:
            origin = next(
                (remote for remote in repo.remotes if remote.name == "origin"), None
            )
            if origin:
                origin.fetch(prune=True)
                log("Fetched latest remote profiles.")
        except GitCommandError as e:
            log(f"Failed to fetch remote: {e}")

    # Get local and remote branches
    local_branches = {branch.name for branch in repo.branches}
    remote_branches = (
        {ref.name.replace("origin/", "") for ref in repo.remotes.origin.refs}
        if repo.remotes
        else set()
    )

    if profile_name in local_branches:
        # Checkout local branch
        repo.git.checkout(profile_name)
        log(f"Switched to profile: {profile_name}")
    elif profile_name in remote_branches:
        # Checkout and track remote branch
        repo.git.checkout("-b", profile_name, f"origin/{profile_name}")
        log(f"Downloaded and Switched to new profile from cloud: {profile_name}")
    else:
        log(f"Profile '{profile_name}' is not available in the repository.")
