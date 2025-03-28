import sys
from pathlib import Path
from dataclasses import dataclass
from git import Repo, GitCommandError, InvalidGitRepositoryError
from dotctl.paths import app_profile_directory
from dotctl.utils import log
from dotctl.exception import exception_handler
from dotctl.handlers.git_handler import (
    get_repo,
    get_repo_branches,
    git_fetch,
    delete_local_branch,
    delete_remote_branch,
    is_remote_repo,
)
from dotctl import __APP_NAME__, __DEFAULT_PROFILE__


@dataclass
class RemoverProps:
    profile: str
    profile_dir: Path
    fetch: bool
    no_confirm: bool


remover_default_props = RemoverProps(
    profile=__DEFAULT_PROFILE__,
    profile_dir=Path(app_profile_directory),
    fetch=False,
    no_confirm=False,
)


@exception_handler
def remove(props: RemoverProps):
    log("Removing profile...")
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

        profile = props.profile

        # Delete local branch if it exists
        if profile in local_profiles:
            delete_local_branch(repo, profile)
            log(f"Local profile '{profile}' removed successfully.")
        else:
            log(f"Profile '{profile}' does not exist locally.")

        # Delete remote branch if it exists
        if is_remote_repo(repo=repo):
            if profile in remote_profiles:
                if props.no_confirm:
                    delete_remote_branch(repo, profile)
                    log(f"Remote profile '{profile}' removed successfully.")
                    return
                else:
                    # Ask for confirmation
                    confirm = input(
                        f"Are you sure you want to delete remote profile '{profile}'? (y/N): "
                    )
                    if confirm.lower() == "y":
                        delete_remote_branch(repo, profile)
                        log(f"Remote profile '{profile}' removed successfully.")
                        return
                    else:
                        log("Remote profile deletion aborted by user.")
                        return

        log(f"Profile '{profile}' does not exist on cloud.")

    except Exception as e:
        raise Exception(f"Unexpected error: {e}")
