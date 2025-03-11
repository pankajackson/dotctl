from pathlib import Path
from dotctl.paths import profile_directory
from dotctl.utils import log
from git import Repo, GitCommandError


def initialise(
    url: str | None = None,
    profile: str | None = None,
    dest: Path = Path(profile_directory),
):
    log("Initializing...")

    dest = dest.resolve()

    if dest is None:
        raise ValueError("Destination path cannot be None")

    if url:
        # Clone the repository
        log(f"Cloning repository from {url} to {dest}...")
        repo = Repo.clone_from(url, dest)

    else:
        # Initialize a new local Git repository
        log(f"Creating a new Git repository at {dest}...")
        dest.mkdir(parents=True, exist_ok=True)
        repo = Repo.init(dest)

        # Ensure a default branch exists
        if not list(dest.glob(".git/refs/heads/*")):  # Check if any branch exists
            default_branch = profile if profile else "main"
            log(f"Setting up default branch '{default_branch}'...")
            repo.git.checkout("-b", default_branch)

    # Checkout to the provided branch if `profile` is specified
    if profile:
        try:
            log(f"Checking out branch '{profile}'...")
            repo.git.checkout(profile)
        except GitCommandError:
            log(f"Branch '{profile}' not found. Creating and switching to it...")
            repo.git.checkout("-b", profile)

    log("Profile initialized successfully.")
