import argparse


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="plasmasaver",
        epilog="Please report bugs at pankajackson@live.co.uk",
    )

    parser.add_argument(
        "-v", "--version", required=False, action="store_true", help="Show version"
    )

    subparsers = parser.add_subparsers(help="Desired action to perform", dest="action")
    save_parser = subparsers.add_parser("save", help="Save current config as a profile")
    remove_parser = subparsers.add_parser("remove", help="Remove the specified profile")
    list_parser = subparsers.add_parser("list", help="Lists created profiles")
    apply_parser = subparsers.add_parser("apply", help="Apply the specified profile")
    import_parser = subparsers.add_parser("import", help="Import a plasmasaver file")
    export_parser = subparsers.add_parser(
        "export", help="Export a profile and share with your friends!"
    )
    wipe_parser = subparsers.add_parser("wipe", help="Wipes all profiles.")

    save_parser.add_argument(
        "profile_name", type=str, help="Name of the profile as a identifier"
    )
    save_parser.add_argument(
        "-f",
        "--force",
        required=False,
        action="store_true",
        help="Overwrite already saved profiles",
    )
    save_parser.add_argument(
        "-c",
        "--config-file",
        required=False,
        type=str,
        help="Use external config file",
        metavar="<path>",
    )
    save_parser.add_argument(
        "-e",
        "--env",
        required=False,
        type=str,
        help="Desktop environment (e.g. kde)",
        metavar="<env>",
    )
    save_parser.add_argument(
        "-p",
        "--password",
        required=False,
        type=str,
        help="Sudo Password to authorize restricted data (e.g. /usr/share)",
        metavar="<password>",
    )
    save_parser.add_argument(
        "--include-global",
        required=False,
        action="store_true",
        help="Include data from global data directory (/usr/share)",
    )
    save_parser.add_argument(
        "--include-sddm",
        required=False,
        action="store_true",
        help="Include sddm data/configs directory (/usr/share/sddm, /etc/sddm.conf.d)",
    )
    save_parser.add_argument(
        "--sddm-only",
        required=False,
        action="store_true",
        help="Perform operation only on sddm data/configurations (Note: sudo password required)",
    )
    save_parser.add_argument(
        "--skip-sudo",
        required=False,
        action="store_true",
        help="Skip all sudo operations",
    )
    remove_parser.add_argument(
        "profile_name", type=str, help="Name of the profile as a identifier"
    )
    apply_parser.add_argument(
        "profile_name", type=str, help="Name of the profile as a identifier"
    )
    apply_parser.add_argument(
        "-p",
        "--password",
        required=False,
        type=str,
        help="Sudo Password to authorize restricted data (e.g. /usr/share)",
        metavar="<password>",
    )
    apply_parser.add_argument(
        "--sddm-only",
        required=False,
        action="store_true",
        help="Perform operation only on sddm data/configurations (Note: sudo password required)",
    )
    apply_parser.add_argument(
        "--skip-global",
        required=False,
        action="store_true",
        help="Skip data from global data directory (/usr/share)",
    )
    apply_parser.add_argument(
        "--skip-sddm",
        required=False,
        action="store_true",
        help="Skip sddm data/configs directory (/usr/share/sddm, /etc/sddm.conf.d)",
    )
    apply_parser.add_argument(
        "--skip-sudo",
        required=False,
        action="store_true",
        help="Skip all sudo operations",
    )
    export_parser.add_argument(
        "profile_name", type=str, help="Name of the profile as a identifier"
    )
    export_parser.add_argument(
        "-p",
        "--password",
        required=False,
        type=str,
        help="Sudo Password to authorize restricted data (e.g. /usr/share)",
        metavar="<password>",
    )
    export_parser.add_argument(
        "--config-only",
        required=False,
        action="store_true",
        help="Perform operation only on plasma configs (skip data, e.g. ~/.config)",
    )
    export_parser.add_argument(
        "--data-only",
        required=False,
        action="store_true",
        help="Perform operation only on plasma data (skip configs, e.g. ~/.local/share)",
    )
    export_parser.add_argument(
        "--sddm-only",
        required=False,
        action="store_true",
        help="Perform operation only on sddm data/configurations (Note: sudo password required)",
    )
    export_parser.add_argument(
        "--skip-global",
        required=False,
        action="store_true",
        help="Skip data from global data directory (/usr/share)",
    )
    export_parser.add_argument(
        "--skip-sddm",
        required=False,
        action="store_true",
        help="Skip sddm data/configs directory (/usr/share/sddm, /etc/sddm.conf.d)",
    )
    export_parser.add_argument(
        "--skip-sudo",
        required=False,
        action="store_true",
        help="Skip all sudo operations",
    )
    import_parser.add_argument(
        "profile_name", type=str, help="Name of the profile as a identifier"
    )
    import_parser.add_argument(
        "-p",
        "--password",
        required=False,
        type=str,
        help="Sudo Password to authorize restricted data (e.g. /usr/share)",
        metavar="<password>",
    )
    import_parser.add_argument(
        "--config-only",
        required=False,
        action="store_true",
        help="Perform operation only on plasma configs (skip data, e.g. ~/.config)",
    )
    import_parser.add_argument(
        "--data-only",
        required=False,
        action="store_true",
        help="Perform operation only on plasma data (skip configs, e.g. ~/.local/share)",
    )
    import_parser.add_argument(
        "--sddm-only",
        required=False,
        action="store_true",
        help="Perform operation only on sddm data/configurations (Note: sudo password required)",
    )
    import_parser.add_argument(
        "--skip-global",
        required=False,
        action="store_true",
        help="Skip data from global data directory (/usr/share)",
    )
    import_parser.add_argument(
        "--skip-sddm",
        required=False,
        action="store_true",
        help="Skip sddm data/configs directory (/usr/share/sddm, /etc/sddm.conf.d)",
    )
    import_parser.add_argument(
        "--skip-sudo",
        required=False,
        action="store_true",
        help="Skip all sudo operations",
    )

    return parser
