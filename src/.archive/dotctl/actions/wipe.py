import shutil
from dotctl.handlers import log
from dotctl.paths import base_profile_dir_path
from dotctl.exception import exception_handler


@exception_handler
def wipe():
    """Wipes all profiles."""
    confirm = input('This will wipe all your profiles. Enter "WIPE" Tto continue: ')
    if confirm == "WIPE":
        shutil.rmtree(base_profile_dir_path)
        log("Removed all profiles!")
    else:
        log("Aborting...")
