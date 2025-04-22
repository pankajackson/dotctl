import shutil
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from dotctl.paths import app_profile_directory
from dotctl.utils import log
from dotctl.exception import exception_handler
from dotctl.handlers.git_handler import get_repo, pull_changes
from dotctl import __APP_NAME__, __DEFAULT_PROFILE__


@dataclass
class PullerProps:
    profile_dir: Path


puller_default_props = PullerProps(
    profile_dir=Path(app_profile_directory),
)


@exception_handler
def pull(props: PullerProps):
    log("Pulling profile changes...")
    repo = get_repo(props.profile_dir)
    try:
        changes = pull_changes(repo)
        if changes is None:
            log("ℹ️ Profile already up to date.")
        elif changes:
            log("✅ Pulled latest changes successfully.")

    except Exception as e:
        raise Exception(f"Unexpected error: {e}")
