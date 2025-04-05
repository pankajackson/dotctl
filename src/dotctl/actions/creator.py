from datetime import datetime
import socket
import sys
from pathlib import Path
from dataclasses import dataclass
from git import Repo, GitCommandError, InvalidGitRepositoryError
from dotctl.paths import app_profile_directory
from dotctl.utils import log
from dotctl.exception import exception_handler
from dotctl.handlers.hooks_handler import hooks_initializer
from dotctl.handlers.config_handler import conf_initializer
from dotctl.handlers.git_handler import (
    add_changes,
    commit_changes,
    get_repo,
    get_repo_branches,
    git_fetch,
    create_branch,
    create_empty_branch,
    is_remote_repo,
    is_repo_changed,
    push_existing_branch,
    push_new_branch,
)
from dotctl import __APP_NAME__, __DEFAULT_PROFILE__


@dataclass
class CreatorProps:
    profile: str
    profile_dir: Path
    fetch: bool
    config: str | Path | None
    env: str | None


creator_default_props = CreatorProps(
    profile=__DEFAULT_PROFILE__,
    profile_dir=Path(app_profile_directory),
    fetch=False,
    config=None,
    env=None,
)


@exception_handler
def create(props: CreatorProps):
    log("Creating profile...")
    repo = get_repo(props.profile_dir)

    if props.fetch:
        git_fetch(repo)

    _, _, _, all_profiles = get_repo_branches(repo)
    if props.profile in all_profiles:
        log(f"Profile '{props.profile}' already exists.")
        return
    if props.env or props.config:
        if props.config is not None and isinstance(props.config, str):
            props.config = Path(props.config)
        create_empty_branch(repo, props.profile)
        conf_initializer(
            env=props.env,
            custom_config=props.config,
        )
        hooks_initializer()
    else:
        create_branch(repo, props.profile)

    add_changes(repo=repo)
    if is_repo_changed(repo=repo):
        hostname = socket.gethostname()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_message = f"{hostname} | Profile Initialized | {timestamp}"
        commit_changes(repo=repo, message=full_message)
        is_remote, _ = is_remote_repo(repo=repo)
        _, remote_profiles, active_profile, all_profiles = get_repo_branches(repo)
        if is_remote:
            if props.profile not in remote_profiles:
                git_fetch(repo=repo)
                _, remote_profiles, active_profile, all_profiles = get_repo_branches(
                    repo
                )
            if not props.profile in remote_profiles:
                push_new_branch(repo=repo)
            else:
                push_existing_branch(repo=repo)

    log(f"Profile '{props.profile}' created and activated successfully.")
