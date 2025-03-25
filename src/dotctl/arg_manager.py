import argparse
from dotctl import __APP_NAME__, __APP_VERSION__
from dotctl.validators import valid_git_url, valid_config_file


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
        type=valid_git_url,
        help="Git repository URL associated with the profile.",
        metavar="<git-url>",
        default=None,
    )

    init_parser.add_argument(
        "-p",
        "--profile",
        type=str,
        help="Profile name identifier. Defaults to the repository’s default branch if not provided.",
        metavar="<profile>",
        default=None,
    )

    init_parser.add_argument(
        "-c",
        "--config",
        type=valid_config_file,
        help="Use external config file.",
        metavar="<path>",
        default=None,
    )

    init_parser.add_argument(
        "-e",
        "--env",
        type=str,
        help="Desktop environment (e.g. kde)",
        metavar="<env>",
        default=None,
    )

    # Save Parser
    save_parser = subparsers.add_parser("save", help="Save current config in a profile")

    save_parser.add_argument(
        "-p",
        "--password",
        type=str,
        help="Sudo Password to authorize restricted data (e.g. /usr/share)",
        metavar="<password>",
        default=None,
    )
    save_parser.add_argument(
        "--skip-sudo",
        required=False,
        action="store_true",
        help="Skip all sudo operations",
    )

    # List Parser
    list_parser = subparsers.add_parser(
        "list", aliases=["ls"], help="Lists created profiles"
    )
    list_parser.add_argument(
        "--details",
        required=False,
        action="store_true",
        help="Display detailed profile information, including status and sync state.",
    )
    list_parser.add_argument(
        "--fetch",
        required=False,
        action="store_true",
        help="Fetch and Sync profile information from Cloud",
    )

    # Switch Parser
    switch_parser = subparsers.add_parser(
        "switch", aliases=["sw"], help="Switches between profiles"
    )
    switch_parser.add_argument(
        "profile",
        nargs="?",  # Makes positional argument optional
        type=str,
        help="Profile to switch to",
        default=None,
    )
    switch_parser.add_argument(
        "--fetch",
        required=False,
        action="store_true",
        help="Fetch and Sync profile information from Cloud before switching to it",
    )

    # Create Parser
    create_parser = subparsers.add_parser(
        "create", aliases=["new"], help="Creates a new profile"
    )
    create_parser.add_argument(
        "profile",
        type=str,
        help="Profile to create",
        default=None,
    )
    create_parser.add_argument(
        "--fetch",
        required=False,
        action="store_true",
        help="Fetch and Sync profile information from Cloud before creating it",
    )

    # Remove Parser
    create_parser = subparsers.add_parser(
        "remove", aliases=["del"], help="Delete existing profile"
    )
    create_parser.add_argument(
        "profile",
        type=str,
        help="Profile to remove",
        default=None,
    )
    create_parser.add_argument(
        "-y",
        "--no-confirm",
        required=False,
        action="store_true",
        help="Remove profile from cloud without confirmation",
        default=False,
    )
    create_parser.add_argument(
        "--fetch",
        required=False,
        action="store_true",
        help="Fetch and Sync profile information from Cloud before removing it",
    )
    return parser
