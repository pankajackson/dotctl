import os
import yaml
import re
import shutil
import fnmatch
from dataclasses import dataclass, field
from pathlib import Path
from dotctl import __BASE_DIR__
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


@dataclass
class EntryConfig:
    entries: list[str]
    location: str
    required_sudo: bool = False
    ignore_patterns: list[str] = field(default_factory=list)


def is_ignored(
    path: str | Path,
    patterns: list[str],
    *,
    base_path: str | Path = Path(),
) -> bool:
    """Match a path relative to the section location, including ignored dirs."""
    if not patterns:
        return False
    path = Path(base_path) / path
    parts = path.parts
    return any(
        fnmatch.fnmatch(path.as_posix(), pattern)
        or any(fnmatch.fnmatch(Path(*parts[:i]).as_posix(), pattern) for i in range(1, len(parts)))
        for pattern in patterns
    )


def patterns_for_entry(entry: str | Path, patterns: list[str]) -> list[str]:
    """Translate section-relative patterns for rsync's entry-relative paths."""
    entry_parts = Path(entry).parts
    relative_patterns = []
    for pattern in patterns:
        pattern_parts = Path(pattern).parts
        if len(pattern_parts) > len(entry_parts) and all(
            fnmatch.fnmatch(entry_part, pattern_part)
            for entry_part, pattern_part in zip(entry_parts, pattern_parts)
        ):
            relative_patterns.append(Path(*pattern_parts[len(entry_parts) :]).as_posix())
        else:
            relative_patterns.append(pattern)
    print("#################### patterns for entry ########################")
    print(relative_patterns)
    return relative_patterns


@dataclass
class Config:
    save: dict[str, EntryConfig]
    export: dict[str, EntryConfig]


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
        "SYS_SHARE_DIR": sys_share_directory,
        "SYS_CONFIG_DIR": sys_config_directory,
    }
}


def parse_keywords(tokens_: dict, token_symbol: str, config: dict):
    for item in config:
        for name in config[item]:
            for key, value in tokens_["keywords"].items():
                word = token_symbol + key
                location = config[item][name]["location"]
                if word in location:
                    config[item][name]["location"] = location.replace(word, value)


def conf_reader(config_file: Path = Path(app_config_file)) -> Config:
    with open(config_file, "r") as text:
        config = yaml.load(text.read(), Loader=yaml.SafeLoader)

    parse_keywords(tokens, TOKEN_SYMBOL, config)

    def load_section(name: str, values: dict) -> EntryConfig:
        if not isinstance(values, dict):
            raise ValueError(f"Config section '{name}' must be a mapping.")
        required_sudo = values.get("required_sudo", False)
        if not isinstance(required_sudo, bool):
            raise ValueError(
                f"Config section '{name}'.required_sudo must be true or false."
            )
        entries = values.get("entries")
        if not isinstance(entries, list) or not all(
            isinstance(entry, str) for entry in entries
        ):
            raise ValueError(
                f"Config section '{name}'.entries must be a list of paths."
            )
        ignore_patterns = values.get("ignore_patterns", [])
        if not isinstance(ignore_patterns, list) or not all(
            isinstance(pattern, str) for pattern in ignore_patterns
        ):
            raise ValueError(
                f"Config section '{name}'.ignore_patterns must be a list of patterns."
            )
        location = values.get("location")
        if not isinstance(location, str):
            raise ValueError(f"Config section '{name}'.location must be a path.")
        return EntryConfig(
            entries=entries,
            location=location,
            required_sudo=required_sudo,
            ignore_patterns=ignore_patterns,
        )

    return Config(
        save={k: load_section(k, v) for k, v in config["save"].items()},
        export={k: load_section(k, v) for k, v in config["export"].items()},
    )


def conf_initializer(
    env: str | None = None,
    custom_config: Path | None = None,
    app_config_file_path: Path = Path(app_config_file),
) -> Path | None:

    if app_config_file_path.exists():
        return None

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
        env = (
            (
                os.environ.get("XDG_CURRENT_DESKTOP")
                or os.environ.get("XDG_SESSION_DESKTOP")
                or os.environ.get("DESKTOP_SESSION")
                or os.environ.get("GDMSESSION")
                or ""
            )
            .split(":")[0]
            .lower()
        )
        if not env:
            log(
                'Unknown Desktop Environment. Use "-e"/"--env" to specify an environment, using default config file.'
            )
            conf_file_name = templates_base_dir / "other.yaml"
        else:
            conf_file_name = templates_base_dir / f"{env}.yaml"
            if not conf_file_name.exists():
                log(
                    f"Template for '{env}' Desktop Environment not exist, using default config file."
                )
                conf_file_name = templates_base_dir / "other.yaml"

    if not conf_file_name.exists():
        raise FileNotFoundError(
            f"Template config file '{conf_file_name}' does not exist."
        )

    try:
        shutil.copyfile(conf_file_name, app_config_file_path)
    except shutil.Error as e:
        raise RuntimeError(f"Failed to copy template config file: {e}")

    return app_config_file_path
