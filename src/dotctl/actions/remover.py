import sys
from pathlib import Path
from dataclasses import dataclass
from git import Repo, GitCommandError, InvalidGitRepositoryError
from dotctl.paths import app_profile_directory
from dotctl.utils import log
from dotctl.exception import exception_handler
from dotctl import __APP_NAME__, __DEFAULT_PROFILE__


@dataclass
class RemoverProps:
    profile: str
    profile_dir: Path
    fetch: bool


remover_default_props = RemoverProps(
    profile=__DEFAULT_PROFILE__,
    profile_dir=Path(app_profile_directory),
    fetch=False,
)


@exception_handler
def remove(props: RemoverProps):
    log("Removing profile...")

    if not props.profile_dir.exists():
        log(f"Profile repo not yet initialized, run `{__APP_NAME__} init` first.")
        sys.exit(1)

    try:
        repo = Repo(props.profile_dir)

        origin = None
        if props.fetch and repo.remotes:
            try:
                origin = next(
                    (remote for remote in repo.remotes if remote.name == "origin"), None
                )
                if origin:
                    origin.fetch(prune=True)
            except GitCommandError as e:
                log(f"Failed to fetch remote: {e}")

        branch_name = props.profile

        # Delete local branch if it exists
        if branch_name in repo.branches:
            repo.delete_head(branch_name, force=True)
            log(f"Local profile '{branch_name}' removed successfully.")
        else:
            log(f"profile '{branch_name}' does not exist locally.")

        # Delete remote branch if it exists
        if origin is None and repo.remotes:
            origin = next(
                (remote for remote in repo.remotes if remote.name == "origin"), None
            )

        if origin:
            remote_branches = [ref.remote_head for ref in origin.refs]
            if branch_name in remote_branches:
                origin.push(refspec=f":refs/heads/{branch_name}")
                log(f"Remote profile '{branch_name}' removed successfully.")
            else:
                log(f"Profile '{branch_name}' does not exist on cloud.")
        else:
            log("No remote 'origin' found to delete the remote profile.")

    except GitCommandError as e:
        log(f"Git command error: {e}")
    except InvalidGitRepositoryError:
        log(f"Profile repo not yet initialized, run `{__APP_NAME__} init` first.")
    except Exception as e:
        raise Exception(f"Unexpected error: {e}")
