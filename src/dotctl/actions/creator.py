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
    create_branch,
)
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
    repo = get_repo(props.profile_dir)

    try:
        if props.fetch:
            git_fetch(repo)

        _, _, _, all_profiles = get_repo_branches(repo)
        if props.profile in all_profiles:
            log(f"Profile '{props.profile}' already exists.")
            return
        create_branch(repo, props.profile)
        log(f"Profile '{props.profile}' created and activated successfully.")
    except Exception as e:
        raise Exception(f"Unexpected error: {e}")
