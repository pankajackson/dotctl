import sys
from pathlib import Path
from dataclasses import dataclass
from git import Repo, GitCommandError, InvalidGitRepositoryError
from dotctl.paths import app_profile_directory
from dotctl.utils import log
from dotctl.exception import exception_handler
from dotctl import __APP_NAME__, __DEFAULT_PROFILE__


@dataclass
class CreatorProps:
    profile: str
    profile_dir: Path
    fetch: bool


creator_default_props = CreatorProps(
    profile=__DEFAULT_PROFILE__,
    profile_dir=Path(app_profile_directory),
    fetch=False,
)


@exception_handler
def create(props: CreatorProps):
    log("Creating profile...")
    if not props.profile_dir.exists():
        log(f"Profile repo not yet initialized, run `{__APP_NAME__} init` first.")
        sys.exit(1)
    try:
        repo = Repo(props.profile_dir)

        if repo.bare:
            raise Exception("Error: The repository is bare. Cannot create a branch.")

        # Check if the branch already exists locally
        if props.profile in repo.branches:
            log(f"Profile '{props.profile}' already exists.")
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

        # Check if the branch exists remotely
        remote_branches = (
            {ref.name.replace("origin/", "") for ref in repo.remotes.origin.refs}
            if repo.remotes
            else set()
        )

        if props.profile in remote_branches:
            log(f"Profile '{props.profile}' already exists on the cloud.")
            return

        # Create a new branch and switch to it
        has_commits = repo.head.is_valid() if repo.head else False
        if not has_commits:
            repo.index.commit("Initial commit for dotctl")
            log("Initial commit created.")

        new_branch = repo.create_head(props.profile)
        new_branch.checkout()
        log(f"Profile '{props.profile}' created and activated successfully.")

    except GitCommandError as e:
        log(f"Git command error: {e}")
    except InvalidGitRepositoryError:
        log(f"Profile repo not yet initialized, run `{__APP_NAME__} init` first.")
    except Exception as e:
        raise Exception(f"Unexpected error: {e}")
