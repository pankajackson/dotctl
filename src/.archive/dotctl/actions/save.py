import os
import yaml
import shutil
from dotctl.handlers import mkdir, log, copy
from dotctl.paths import base_profile_dir_path, plasmasaver_config_file_path
from dotctl.confs import read_plasmasaver_config
from dotctl.exception import exception_handler


@exception_handler
def save_profile(
    name,
    profile_list,
    force=False,
    include_global=False,
    include_sddm=False,
    sddm_only=False,
):
    # assert
    assert name not in profile_list or force, "Profile with this name already exists"

    # run
    log("saving profile...")
    profile_dir = os.path.join(base_profile_dir_path, name)
    mkdir(profile_dir)
    with open(plasmasaver_config_file_path, "r") as configs:
        plasmasaver_config = yaml.safe_load(configs)
        if sddm_only:
            plasmasaver_config["export"] = {
                "sddm": plasmasaver_config["export"]["sddm"]
            }
            plasmasaver_config["save"] = {
                "sddm_configs": plasmasaver_config["save"]["sddm_configs"]
            }
        else:
            if not include_global:
                plasmasaver_config["export"].pop("root_share_folder", None)
            if not include_sddm:
                plasmasaver_config["export"].pop("sddm", None)
                plasmasaver_config["save"].pop("sddm_configs", None)

        with open(os.path.join(profile_dir, "conf.yaml"), "w") as outfile:
            yaml.dump(plasmasaver_config, outfile, default_flow_style=False)
    plasmasaver_config = read_plasmasaver_config(os.path.join(profile_dir, "conf.yaml"))
    for section in plasmasaver_config["save"]:
        location = plasmasaver_config["save"][section]["location"]
        folder = os.path.join(profile_dir, section)
        mkdir(folder)
        for entry in plasmasaver_config["save"][section]["entries"]:
            source = os.path.join(location, entry)
            dest = os.path.join(folder, entry)
            if os.path.exists(source):
                if os.path.isdir(source):
                    copy(source, dest)
                else:
                    shutil.copy(source, dest)

    log("Profile saved successfully!")
