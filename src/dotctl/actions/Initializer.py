from pathlib import Path
from dataclasses import dataclass, replace
from dotctl.paths import app_profile_directory, app_config_file
from dotctl.utils import log
from dotctl.handlers.config_handler import conf_initializer
from git import Repo, GitCommandError


@dataclass
class InitializerProps:
    custom_config: Path | None
    git_url: str | None
    profile: str | None
    env: str
    dest: Path


initializer_default_props = InitializerProps(
    custom_config=None,
    git_url=None,
    profile=None,
    env="other",
    dest=Path(app_profile_directory),
)


def initialise(props: InitializerProps):
    log("Initializing...")

    dest = props.dest.resolve()

    if dest is None:
        raise ValueError("Destination path cannot be None")

    if props.git_url:
        # Clone the repository
        log(f"Cloning repository from {props.git_url} to {dest}...")
        repo = Repo.clone_from(props.git_url, dest)

    else:
        # Initialize a new local Git repository
        log(f"Creating a new Git repository at {dest}...")
        dest.mkdir(parents=True, exist_ok=True)
        repo = Repo.init(dest)

        # Ensure a default branch exists
        if not list(dest.glob(".git/refs/heads/*")):  # Check if any branch exists
            default_branch = props.profile if props.profile else "main"
            log(f"Setting up default branch '{default_branch}'...")
            repo.git.checkout("-b", default_branch)

    # Checkout to the provided branch if `profile` is specified
    if props.profile:
        try:
            log(f"Checking out branch '{props.profile}'...")
            repo.git.checkout(props.profile)
        except GitCommandError:
            log(f"Branch '{props.profile}' not found. Creating and switching to it...")
            repo.git.checkout("-b", props.profile)

    conf_initializer(
        env=props.env,
        custom_config=props.custom_config,
    )
    log("Profile initialized successfully.")
