import os
import shutil
from dotctl.handlers import log, mkdir, copy
from dotctl.paths import base_profile_dir_path, home_path, temp_path
from dotctl.exception import exception_handler
from dotctl.confs import read_plasmasaver_config, EXPORT_EXTENSION, sudo_pass, skip_sudo
from dotctl.handlers import get_sudo_pass
import subprocess
from zipfile import is_zipfile, ZipFile


@exception_handler
def import_profile(
    path,
    skip_global=False,
    skip_sddm=False,
    sddm_only=False,
    config_only=False,
    data_only=False,
):
    # assert
    assert (
        is_zipfile(path) and path[-5:] == EXPORT_EXTENSION
    ), "Not a valid plasmasaver file"
    item = os.path.basename(path)[:-5]
    assert not os.path.exists(
        os.path.join(base_profile_dir_path, item)
    ), "A profile with this name already exists"

    # run
    log("Importing profile. It might take a minute or two...")

    item = os.path.basename(path).replace(EXPORT_EXTENSION, "")

    with ZipFile(path, "r") as zip_file:
        zip_file.extractall(temp_path)

    config_file_location = os.path.join(temp_path, "conf.yaml")
    plasmasaver_config = read_plasmasaver_config(config_file_location)

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
        plasmasaver_config["export"] = {"sddm": plasmasaver_config["export"]["sddm"]}
        plasmasaver_config["save"] = {
            "sddm_configs": plasmasaver_config["save"]["sddm_configs"]
        }

    profile_dir = os.path.join(base_profile_dir_path, item)
    copy(os.path.join(temp_path, "save"), profile_dir)
    shutil.copy(os.path.join(temp_path, "conf.yaml"), profile_dir)

    for section in plasmasaver_config["export"]:
        location = plasmasaver_config["export"][section]["location"]
        path = os.path.join(temp_path, "export", section)
        mkdir(path)
        for entry in plasmasaver_config["export"][section]["entries"]:
            source = os.path.join(path, entry)
            dest = os.path.join(location, entry)
            log(f'Importing "{section}/{entry}"...')
            if os.path.exists(source):
                if os.path.isdir(source):
                    copy(source, dest)
                else:
                    try:
                        shutil.copy(source, dest)
                    except PermissionError:
                        command = "cp %s %s" % (source, dest)
                        if sudo_pass:
                            subprocess.check_output(
                                "echo %s|sudo -S %s; echo $? " % (sudo_pass, command),
                                shell=True,
                            )
                        elif skip_sudo:
                            pass
                        else:
                            temp_pass = get_sudo_pass(dest)
                            subprocess.check_output(
                                "echo %s|sudo -S %s; echo $? " % (temp_pass, command),
                                shell=True,
                            )

    shutil.rmtree(temp_path)

    log("Profile successfully imported!")
