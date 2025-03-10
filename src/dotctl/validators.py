import argparse
import re


def valid_git_url(url: str) -> str:
    if url is None:
        return None

    is_valid = bool(re.match(r"^(https?://|git@[\w.-]+:[\w./-]+\.git$)", url))

    if not is_valid:
        raise argparse.ArgumentTypeError(f"Invalid Git URL: {url}")

    return url
