import os
import yaml
import re
import shutil
from dotctl.exception import exception_handler
from dotctl.paths import (
    home_path,
    config_dir_path,
    share_dir_path,
    root_share_dir,
    bin_dir_path,
    sddm_dir,
    system_config_dir,
    base_plasmasaver_dir,
    base_profile_dir_path,
    plasmasaver_config_file_path,
)

EXPORT_EXTENSION = ".plsv"
sudo_pass = None
skip_sudo = False


def ends_with(grouped_regex, path) -> str:
    occurrence = re.search(grouped_regex, path).group()
    dirs = os.listdir(path[0 : path.find(occurrence)])
    ends_with_text = re.search(grouped_regex, occurrence).group(2)
    for directory in dirs:
        if directory.endswith(ends_with_text):
            return path.replace(occurrence, directory)
    return occurrence


def begins_with(grouped_regex, path) -> str:
    occurrence = re.search(grouped_regex, path).group()
    dirs = os.listdir(path[0 : path.find(occurrence)])
    ends_with_text = re.search(grouped_regex, occurrence).group(2)
    for directory in dirs:
        if directory.startswith(ends_with_text):
            return path.replace(occurrence, directory)
    return occurrence


TOKEN_SYMBOL = "$"
tokens = {
    "keywords": {
        "dict": {
            "HOME": home_path,
            "CONFIG_DIR": config_dir_path,
            "SHARE_DIR": share_dir_path,
            "ROOT_SHARE_DIR": root_share_dir,
            "BIN_DIR": bin_dir_path,
            "PLASMA_SAVER_DIR": base_plasmasaver_dir,
            "SDDM_DIR": sddm_dir,
            "SYS_CONFIG_DIR": system_config_dir,
        }
    }
}


def parse_keywords(tokens_, token_symbol, parsed):
    for item in parsed:
        for name in parsed[item]:
            for key, value in tokens_["keywords"]["dict"].items():
                word = token_symbol + key
                location = parsed[item][name]["location"]
                if word in location:
                    parsed[item][name]["location"] = location.replace(word, value)


@exception_handler
def read_plasmasaver_config(config_file=plasmasaver_config_file_path) -> dict:
    with open(config_file, "r") as text:
        plasmasaver = yaml.load(text.read(), Loader=yaml.SafeLoader)
    parse_keywords(tokens, TOKEN_SYMBOL, plasmasaver)

    return plasmasaver


def conf_initializer(env="NONE"):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    kde_conf_path = os.path.join(base_dir, "templates/kde.yml")
    other_conf_path = os.path.join(base_dir, "templates/other.yml")

    if not os.path.exists(plasmasaver_config_file_path) or (env and (env != "NONE")):
        if os.path.expandvars("$XDG_CURRENT_DESKTOP") == "KDE" or env.upper() == "KDE":
            conf_path = kde_conf_path
        else:
            print(
                f'plasmasaver: Unknown Desktop environment, please use "-e"/"--env" to specify environment with "save" command to initialize base config.'
            )
            conf_path = other_conf_path
        shutil.copyfile(conf_path, plasmasaver_config_file_path)
    return plasmasaver_config_file_path
