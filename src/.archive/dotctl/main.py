import os
from importlib.metadata import version as pkg_version, PackageNotFoundError
from .arg_manager import get_parser
from .exception import exception_handler
from .confs import conf_initializer, sudo_pass, skip_sudo
from .paths import base_profile_dir_path, plasmasaver_config_file_path
from .actions import (
    list_profiles,
    save_profile,
    apply_profile,
    remove_profile,
    export,
    import_profile,
    wipe,
)

try:
    import yaml
except ModuleNotFoundError as error:
    raise ModuleNotFoundError(
        "Please install the module PyYAML using pip: \n" "pip install PyYAML"
    ) from error


if not os.path.exists(base_profile_dir_path):
    os.makedirs(base_profile_dir_path)

list_of_profiles = os.listdir(base_profile_dir_path)
length_of_lop = len(list_of_profiles)
try:
    version = pkg_version("dotctl")
except PackageNotFoundError:
    version = "0.0.0"


@exception_handler
def main():
    """The main function that handles all the arguments and options."""

    parser = get_parser()
    args = parser.parse_args()
    global skip_sudo
    skip_sudo = False
    global sudo_pass
    sudo_pass = None
    conf_initializer()

    if args.action == "save":
        if args.password and args.skip_sudo:
            raise Exception(
                "error: -p/--password and --skip-sudo can't be used at the same time"
            )
        elif args.skip_sudo:
            skip_sudo = True
        elif args.password:
            sudo_pass = args.password
        if (args.sddm_only and args.include_sddm) or (
            args.sddm_only and args.include_global
        ):
            raise Exception(
                "error: --sddm-only can't be used with --include-sddm and --include-global"
            )
        if args.env:
            conf_initializer(args.env)
        if args.config_file:
            if not os.path.exists(args.config_file):
                raise Exception(
                    "error: invalid config file path, The path given in arg doesn't exist or is not accessible: %s"
                    % args.config_file
                )
            with open(args.config_file, "r") as configs:
                e_conf = yaml.safe_load(configs)
                if "export" not in e_conf.keys() or "save" not in e_conf.keys():
                    raise Exception(
                        'error: missing config block(s), "save" and "export" are core blocks of plasmasaver configuration'
                    )
            if e_conf:
                global plasmasaver_config_file_path
                plasmasaver_config_file_path = args.config_file
        save_profile(
            args.profile_name,
            list_of_profiles,
            force=args.force,
            include_sddm=args.include_sddm,
            include_global=args.include_global,
            sddm_only=args.sddm_only,
        )
    elif args.action == "remove":
        remove_profile(args.profile_name, list_of_profiles, length_of_lop)

    elif args.action == "list":
        list_profiles(list_of_profiles, length_of_lop)

    elif args.action == "apply":
        if args.password and args.skip_sudo:
            raise Exception(
                "error: -p/--password and --skip-sudo can't be used at the same time"
            )
        elif args.skip_sudo:
            skip_sudo = True
        elif args.password:
            sudo_pass = args.password
        if (args.sddm_only and args.skip_sddm) or (args.sddm_only and args.skip_global):
            raise Exception(
                "error: --sddm-only can't be used with --include-sddm and --include-global"
            )
        apply_profile(
            args.profile_name,
            list_of_profiles,
            length_of_lop,
            skip_sddm=args.skip_sddm,
            skip_global=args.skip_global,
            sddm_only=args.sddm_only,
        )

    elif args.action == "import":
        if args.password and args.skip_sudo:
            raise Exception(
                "error: -p/--password and --skip-sudo can't be used at the same time"
            )
        elif args.skip_sudo:
            skip_sudo = True
        elif args.password:
            sudo_pass = args.password
        if (args.sddm_only and args.skip_sddm) or (args.sddm_only and args.skip_global):
            raise Exception(
                "error: --sddm-only can't be used with --include-sddm and --include-global"
            )
        if args.data_only and args.config_only:
            raise Exception(
                "error: --data-only and --config-only can't be used at the same time"
            )
        import_profile(
            args.profile_name,
            skip_global=args.skip_global,
            skip_sddm=args.skip_sddm,
            sddm_only=args.sddm_only,
            config_only=args.config_only,
            data_only=args.data_only,
        )

    elif args.action == "export":
        if args.password and args.skip_sudo:
            raise Exception(
                "error: -p/--password and --skip-sudo can't be used at the same time"
            )
        elif args.skip_sudo:
            skip_sudo = True
        elif args.password:
            sudo_pass = args.password
        if (args.sddm_only and args.skip_sddm) or (args.sddm_only and args.skip_global):
            raise Exception(
                "error: --sddm-only can't be used with --include-sddm and --include-global"
            )
        if args.data_only and args.config_only:
            raise Exception(
                "error: --data-only and --config-only can't be used at the same time"
            )
        export(
            args.profile_name,
            list_of_profiles,
            length_of_lop,
            skip_global=args.skip_global,
            skip_sddm=args.skip_sddm,
            sddm_only=args.sddm_only,
            config_only=args.config_only,
            data_only=args.data_only,
        )

    elif args.version:
        print(f"plasmasaver: {version}")

    elif args.action == "wipe":
        wipe()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
