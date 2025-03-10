import os
import yaml
import shutil
from dotctl.handlers import mkdir, log, copy
from dotctl.paths import base_profile_dir_path
from dotctl.confs import read_plasmasaver_config
from dotctl.exception import exception_handler


@exception_handler
def apply_profile(
    profile_name,
    profile_list,
    profile_count,
    skip_sddm=False,
    skip_global=False,
    sddm_only=False,
):
    # assert
    assert profile_count != 0, "No profile saved yet."
    assert profile_name in profile_list, "Profile not found :("

    # run
    profile_dir = os.path.join(base_profile_dir_path, profile_name)

    log("copying files...")

    config_location = os.path.join(profile_dir, "conf.yaml")
    profile_config = read_plasmasaver_config(config_location)
    if sddm_only:
        profile_config["export"] = {"sddm": profile_config["export"]["sddm"]}
        profile_config["save"] = {
            "sddm_configs": profile_config["save"]["sddm_configs"]
        }
    else:
        if skip_global:
            profile_config["export"].pop("root_share_folder", None)
        if skip_sddm:
            profile_config["export"].pop("sddm", None)
            profile_config["save"].pop("sddm_configs", None)
    for name in profile_config["save"]:
        location = os.path.join(profile_dir, name)
        copy(location, profile_config["save"][name]["location"])

    log(
        "Profile applied successfully! Please log-out and log-in to see the changes completely!"
    )
