import shutil
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from dotctl.paths import app_profile_directory
from dotctl.utils import log
from dotctl.exception import exception_handler
from dotctl.handlers.git_handler import get_repo
from dotctl import __APP_NAME__, __DEFAULT_PROFILE__


@dataclass
class WiperProps:
    no_confirm: bool
    profile_dir: Path


wiper_default_props = WiperProps(
    no_confirm=False,
    profile_dir=Path(app_profile_directory),
)


@exception_handler
def wipe(props: WiperProps):
    log("Wiping profile...")
    get_repo(props.profile_dir)

    try:
        if props.no_confirm:
            shutil.rmtree(props.profile_dir)
            log(f"Profile directory '{props.profile_dir}' removed successfully.")
            return
        else:
            # Ask for confirmation
            confirm = input(f"Are you sure you want to wipe out profile? (y/N): ")
            if confirm.lower() == "y":
                create_backup = input(
                    f"Do you want to create a backup of your profiles? (y/N): "
                )
                if create_backup.lower() == "y":
                    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    backup_dir = f"{props.profile_dir}_backup_{timestamp}"
                    shutil.copytree(props.profile_dir, backup_dir)
                    log(f"Backup directory '{backup_dir}' created successfully.")
                shutil.rmtree(props.profile_dir)
                log(f"Profile directory '{props.profile_dir}' removed successfully.")
                return
            else:
                log("Profile wipe process aborted by user.")
                return
    except Exception as e:
        raise Exception(f"Unexpected error: {e}")
