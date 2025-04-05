from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
import socket
from dotctl.paths import app_profile_directory
from dotctl.utils import log
from dotctl.handlers.config_handler import conf_initializer
from dotctl.handlers.hooks_handler import hooks_initializer
from dotctl.handlers.git_handler import (
    add_changes,
    commit_changes,
    get_repo_branches,
    git_fetch,
    is_git_repo,
    clone_repo,
    create_local_repo,
    checkout_branch,
    is_remote_repo,
    is_repo_changed,
    push_existing_branch,
    push_new_branch,
)
from dotctl.exception import exception_handler
from dotctl import __DEFAULT_PROFILE__


@dataclass
class InitializerProps:
    config: str | Path | None
    git_url: str | None
    profile: str | None
    env: str | None
    dest: Path


initializer_default_props = InitializerProps(
    config=None,
    git_url=None,
    profile=None,
    env=None,
    dest=Path(app_profile_directory),
)


@exception_handler
def initialise(props: InitializerProps):
    log("Initializing...")

    if is_git_repo(props.dest):
        log("Repository already initialized.")
        return

    if props.git_url:
        # Clone the repository
        log(f"Cloning repository from {props.git_url} to {props.dest}...")
        repo = clone_repo(props.git_url, props.dest)

    else:
        # Initialize a new local Git repository
        log(f"Creating a new Git repository at {props.dest}...")
        repo = create_local_repo(props.dest)

    # Checkout to the provided branch if `profile` is specified

    if repo is None:
        raise Exception(f"Failed to initialize profile repo at {props.dest}. ")
    if props.profile:
        checkout_branch(repo, props.profile)

    if props.config is not None and isinstance(props.config, str):
        props.config = Path(props.config)

    conf_initializer(
        env=props.env,
        custom_config=props.config,
    )
    hooks_initializer()
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

    log("Profile initialized successfully.")
