import os
import shutil
from dotctl.handlers import log
from dotctl.paths import base_profile_dir_path
from dotctl.exception import exception_handler


@exception_handler
def remove_profile(profile_name, profile_list, profile_count):
    # assert
    assert profile_count != 0, "No profile saved yet."
    assert profile_name in profile_list, "Profile not found."

    # run
    log("removing profile...")
    shutil.rmtree(os.path.join(base_profile_dir_path, profile_name))
    log("removed profile successfully")
