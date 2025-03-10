import argparse
from dotctl import __APP_NAME__, __APP_VERSION__


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=__APP_NAME__,
        epilog="Please report bugs at https://github.com/pankajackson/dotctl/issues",
    )

    parser.add_argument(
        "-v", "--version", required=False, action="store_true", help="Show version"
    )

    subparsers = parser.add_subparsers(help="Desired action to perform", dest="action")

    # Init parser
    init_parser = subparsers.add_parser("init", help="Initialise a profile")
    init_parser.add_argument(
        "-u",
        "--url",
        type=str,
        required=True,  # Assuming URL is mandatory
        help="Git repository URL associated with the profile",
        metavar="<git-url>",
    )

    init_parser.add_argument(
        "--profile",
        type=str,
        help="Profile name identifier. Defaults to the repository’s default branch if not provided.",
        metavar="<profile>",
    )

    return parser
