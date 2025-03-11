import os
import yaml
import re
import shutil
from pathlib import Path
from dotctl import __BASE_DIR__
from dotctl.exception import exception_handler
from dotctl.paths import (
    home_path,
    config_directory,
    share_directory,
    bin_directory,
    sys_config_directory,
    sys_share_directory,
    app_home_directory,
    app_config_file,
)
from dotctl.utils import log

EXPORT_EXTENSION = ".dtsv"


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
        "HOME": home_path,
        "APP_DIR": app_home_directory,
        "CONFIG_DIR": config_directory,
        "SHARE_DIR": share_directory,
        "BIN_DIR": bin_directory,
        "ROOT_SHARE_DIR": sys_share_directory,
        "SYS_CONFIG_DIR": sys_config_directory,
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
def read_plasmasaver_config(config_file=app_config_file) -> dict:
    with open(config_file, "r") as text:
        plasmasaver = yaml.load(text.read(), Loader=yaml.SafeLoader)
    parse_keywords(tokens, TOKEN_SYMBOL, plasmasaver)

    return plasmasaver


def conf_initializer(
    env: str | None = None,
    custom_config: Path | None = None,
    app_config_file_path: Path = Path(app_config_file),
) -> Path:

    if app_config_file_path.exists():
        return app_config_file_path

    if custom_config:
        log(f"Using custom config file: {custom_config}")
        custom_config = custom_config.resolve()
        if not custom_config.exists():
            raise ValueError(f"Config file '{custom_config}' does not exist.")
        try:
            shutil.copyfile(custom_config, app_config_file_path)
        except shutil.Error as e:
            raise RuntimeError(f"Failed to copy config file: {e}")
        return app_config_file_path

    templates_base_dir = Path(__BASE_DIR__) / "templates"
    templates_base_dir = templates_base_dir.resolve()

    if env:
        conf_file_name = templates_base_dir / f"{env}.yaml"
        if not conf_file_name.exists():
            log(f"Invalid Desktop Environment '{env}', using default config file.")
            conf_file_name = templates_base_dir / "other.yaml"

    else:
        env = os.environ.get("XDG_CURRENT_DESKTOP", "").split(":")[0].lower()
        if not env:
            log(
                'Unknown Desktop Environment. Use "-e"/"--env" to specify an environment, using default config file.'
            )
            conf_file_name = templates_base_dir / "other.yaml"
        else:
            conf_file_name = templates_base_dir / f"{env}.yaml"

    if not conf_file_name.exists():
        raise FileNotFoundError(
            f"Template config file '{conf_file_name}' does not exist."
        )

    try:
        shutil.copyfile(conf_file_name, app_config_file_path)
    except shutil.Error as e:
        raise RuntimeError(f"Failed to copy template config file: {e}")

    return app_config_file_path
