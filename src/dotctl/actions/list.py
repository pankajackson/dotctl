import os
from dotctl.exception import exception_handler
from dotctl.paths import base_profile_dir_path


@exception_handler
def list_profiles(profile_list, profile_count):
    # assert
    assert (
        os.path.exists(base_profile_dir_path) and profile_count != 0
    ), "No profile found."

    # run
    print("Plasmasaver profiles:")
    print("ID\tNAME")
    for i, item in enumerate(profile_list):
        print(f"{i + 1}\t{item}")
