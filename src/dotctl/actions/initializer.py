from pathlib import Path
from dataclasses import dataclass
from dotctl.paths import app_profile_directory
from dotctl.utils import log
from dotctl.handlers.config_handler import conf_initializer
from dotctl.handlers.hooks_handler import hooks_initializer
from dotctl.handlers.git_handler import (
    is_git_repo,
    clone_repo,
    create_local_repo,
    checkout_branch,
)
from dotctl.exception import exception_handler
from dotctl import __DEFAULT_PROFILE__


@dataclass
class InitializerProps:
    custom_config: Path | None
    git_url: str | None
    profile: str | None
    env: str | None
    dest: Path


initializer_default_props = InitializerProps(
    custom_config=None,
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

    conf_initializer(
        env=props.env,
        custom_config=props.custom_config,
    )
    hooks_initializer()
    log("Profile initialized successfully.")
