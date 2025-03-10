import os
import shutil
import yaml
from random import shuffle
from dotctl.handlers import log, mkdir, copy
from dotctl.paths import base_profile_dir_path, home_path
from dotctl.exception import exception_handler
from dotctl.confs import read_plasmasaver_config, EXPORT_EXTENSION


@exception_handler
def export(
    profile_name,
    profile_list,
    profile_count,
    skip_global=False,
    skip_sddm=False,
    sddm_only=False,
    config_only=False,
    data_only=False,
):
    # assert
    assert profile_count != 0, "No profile saved yet."
    assert profile_name in profile_list, "Profile not found."

    # run
    profile_dir = os.path.join(base_profile_dir_path, profile_name)
    export_path = os.path.join(home_path, profile_name)

    if os.path.exists(export_path):
        rand_str = list("abcdefg12345")
        shuffle(rand_str)
        export_path = export_path + "".join(rand_str)
    mkdir(export_path)

    # compressing the files as zip
    log("Exporting profile. It might take a minute or two...")

    profile_config_file = os.path.join(profile_dir, "conf.yaml")
    with open(profile_config_file, "r") as configs:
        plasmasaver_config = yaml.safe_load(configs)

        if skip_global:
            plasmasaver_config["export"].pop("root_share_folder", None)
        if data_only:
            plasmasaver_config.pop("save", None)
        if config_only:
            plasmasaver_config.pop("export", None)
        if skip_sddm:
            plasmasaver_config["export"].pop("sddm", None)
            plasmasaver_config["save"].pop("sddm_configs", None)
        if sddm_only:
            plasmasaver_config["export"] = {
                "sddm": plasmasaver_config["export"]["sddm"]
            }
            plasmasaver_config["save"] = {
                "sddm_configs": plasmasaver_config["save"]["sddm_configs"]
            }

        with open(os.path.join(export_path, "conf.yaml"), "w") as outfile:
            yaml.dump(plasmasaver_config, outfile, default_flow_style=False)

    plasmasaver_config = read_plasmasaver_config(os.path.join(export_path, "conf.yaml"))

    export_path_save = mkdir(os.path.join(export_path, "save"))
    for name in plasmasaver_config["save"]:
        location = os.path.join(profile_dir, name)
        log(f'Exporting "{name}"...')
        copy(location, os.path.join(export_path_save, name))

    plasmasaver_config_export = plasmasaver_config["export"]
    export_path_export = mkdir(os.path.join(export_path, "export"))
    for name in plasmasaver_config_export:
        location = plasmasaver_config_export[name]["location"]
        path = mkdir(os.path.join(export_path_export, name))
        for entry in plasmasaver_config_export[name]["entries"]:
            source = os.path.join(location, entry)
            dest = os.path.join(path, entry)
            log(f'Exporting "{name}/{entry}"...')
            if os.path.exists(source):
                if os.path.isdir(source):
                    copy(source, dest)
                else:
                    shutil.copy(source, dest)

    log("Creating archive")
    shutil.make_archive(export_path, "zip", export_path)

    shutil.rmtree(export_path)
    shutil.move(export_path + ".zip", export_path + EXPORT_EXTENSION)

    log(f"Successfully exported to {export_path}{EXPORT_EXTENSION}")
