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
    save_parser.add_argument(
        "profile",
        nargs="?",  # Makes positional argument optional
        type=str,
        help="Profile to save to",
        default=None,
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
    remove_parser = subparsers.add_parser(
        "remove", aliases=["del", "delete", "rm"], help="Delete existing profile"
    )
    remove_parser.add_argument(
        "profile",
        type=str,
        help="Profile to remove",
        default=None,
    )
    remove_parser.add_argument(
        "-y",
        "--no-confirm",
        required=False,
        action="store_true",
        help="Remove profile from cloud without confirmation",
        default=False,
    )
    remove_parser.add_argument(
        "--fetch",
        required=False,
        action="store_true",
        help="Fetch and Sync profile information from Cloud before removing it",
    )

    # Apply Parser
    apply_parser = subparsers.add_parser("apply", help="Apply profile")

    apply_parser.add_argument(
        "-p",
        "--password",
        type=str,
        help="Sudo Password to authorize restricted data (e.g. /usr/share)",
        metavar="<password>",
        default=None,
    )
    apply_parser.add_argument(
        "--skip-sudo",
        required=False,
        action="store_true",
        help="Skip all sudo operations",
    )
    apply_parser.add_argument(
        "profile",
        nargs="?",  # Makes positional argument optional
        type=str,
        help="Profile to apply to",
        default=None,
    )
    apply_parser.add_argument(
        "--skip-hooks",
        required=False,
        action="store_true",
        help="Skip all hooks",
    )
    apply_parser.add_argument(
        "--skip-pre-hooks",
        required=False,
        action="store_true",
        help="Skip pre hooks",
    )
    apply_parser.add_argument(
        "--skip-post-hooks",
        required=False,
        action="store_true",
        help="Skip post hooks",
    )
    apply_parser.add_argument(
        "--ignore-hook-errors",
        required=False,
        action="store_true",
        help="Ignore hooks errors",
    )

    # Export Parser
    export_parser = subparsers.add_parser("export", help="Export profile")

    export_parser.add_argument(
        "profile",
        nargs="?",  # Makes positional argument optional
        type=str,
        help="Profile to export to",
        default=None,
    )
    export_parser.add_argument(
        "-p",
        "--password",
        type=str,
        help="Sudo Password to authorize restricted data (e.g. /usr/share)",
        metavar="<password>",
        default=None,
    )
    export_parser.add_argument(
        "--skip-sudo",
        required=False,
        action="store_true",
        help="Skip all sudo operations",
    )
    # Import Parser
    import_parser = subparsers.add_parser("import", help="Import profile")

    import_parser.add_argument(
        "profile",
        type=str,
        help="Path of dtsv dot profile file to import",
    )
    import_parser.add_argument(
        "-p",
        "--password",
        type=str,
        help="Sudo Password to authorize restricted data (e.g. /usr/share)",
        metavar="<password>",
        default=None,
    )
    import_parser.add_argument(
        "--skip-sudo",
        required=False,
        action="store_true",
        help="Skip all sudo operations",
    )
    # Wipe Parser
    wipe_parser = subparsers.add_parser("wipe", help="Wipe Profiles")

    wipe_parser.add_argument(
        "-y",
        "--no-confirm",
        required=False,
        action="store_true",
        help="Wipe Profiles without confirmation",
        default=False,
    )
    return parser
