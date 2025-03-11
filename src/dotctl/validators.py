import argparse
import re
from pathlib import Path
import yaml


def valid_git_url(url: str) -> str:
    if url is None:
        return None

    is_valid = bool(re.match(r"^(https?://|git@[\w.-]+:[\w./-]+\.git$)", url))

    if not is_valid:
        raise argparse.ArgumentTypeError(f"Invalid Git URL: {url}")

    return url


def valid_config_file(config: str) -> str:
    config_path = Path(config).resolve()

    if not config_path.exists():
        raise argparse.ArgumentTypeError(f"Config file '{config_path}' does not exist.")

    try:
        with config_path.open("r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise argparse.ArgumentTypeError(f"Invalid YAML format in '{config_path}': {e}")

    if not isinstance(config_data, dict):
        raise argparse.ArgumentTypeError(
            f"Config file '{config_path}' must be a dictionary."
        )

    valid_keys = {"save", "export"}
    invalid_keys = set(config_data.keys()) - valid_keys

    if invalid_keys:
        raise argparse.ArgumentTypeError(
            f"Config file '{config_path}' contains invalid keys: {', '.join(invalid_keys)}. "
            f"Allowed keys are: {', '.join(valid_keys)}."
        )

    return config
