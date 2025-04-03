from enum import Enum
from pathlib import Path
from dataclasses import replace
from .arg_manager import get_parser
from .exception import exception_handler
from .actions.initializer import initialise, initializer_default_props
from .actions.saver import save, saver_default_props
from .actions.activator import apply, activator_default_props
from .actions.lister import get_profile_list, lister_default_props
from .actions.switcher import switch, switcher_default_props
from .actions.creator import create, creator_default_props
from .actions.remover import remove, remover_default_props
from .actions.exporter import exporter, exporter_default_props
from .actions.importer import importer, importer_default_props


class Action(Enum):
    init = "init"
    list = "list"
    switch = "switch"
    save = "save"
    apply = "apply"
    create = "create"
    remove = "remove"
    imp = "import"
    exp = "export"
    help = "help"
    version = "version"


class DotCtl:
    def __init__(
        self,
        action: Action,
        git_url: str | None = None,
        profile: str | None = None,
        config: str | None = None,
        env: str | None = None,
        skip_sudo: bool = False,
        password: str | None = None,
        details: bool = False,
        fetch: bool = False,
        no_confirm: bool = False,
        *args,
        **kwargs,
    ):
        self.action = action
        self.git_url = git_url
        self.profile = profile
        self.config = config
        self.env = str(env) if env else None
        self.skip_sudo = skip_sudo
        self.password = password
        self.details = details
        self.fetch = fetch
        self.no_confirm = no_confirm

    def run(self):
        if self.action == Action.init:
            self.init_profile()
        elif self.action == Action.save:
            self.save_dots()
        elif self.action == Action.apply:
            self.apply_dots()
        elif self.action == Action.list:
            self.list_profiles()
        elif self.action == Action.switch:
            self.switch_profile()
        elif self.action == Action.create:
            self.create_profile()
        elif self.action == Action.remove:
            self.remove_profile()
        elif self.action == Action.exp:
            self.export_profile()
        elif self.action == Action.imp:
            self.import_profile()

    def init_profile(self):
        initializer_props_dict = {}

        if self.git_url:
            initializer_props_dict["git_url"] = self.git_url
        if self.profile:
            initializer_props_dict["profile"] = self.profile
        if self.config:
            initializer_props_dict["custom_config"] = Path(self.config)
        if self.env:
            initializer_props_dict["env"] = self.env

        initializer_props = replace(initializer_default_props, **initializer_props_dict)

        initialise(initializer_props)

    def save_dots(self):
        saver_props_dict = {}
        if self.skip_sudo:
            saver_props_dict["skip_sudo"] = self.skip_sudo
        if self.password:
            saver_props_dict["password"] = self.password
        if self.profile:
            saver_props_dict["profile"] = self.profile
        saver_props = replace(saver_default_props, **saver_props_dict)
        save(saver_props)

    def apply_dots(self):
        apply_props_dict = {}
        if self.skip_sudo:
            apply_props_dict["skip_sudo"] = self.skip_sudo
        if self.password:
            apply_props_dict["password"] = self.password
        if self.profile:
            apply_props_dict["profile"] = self.profile
        apply_props = replace(activator_default_props, **apply_props_dict)
        apply(apply_props)

    def list_profiles(self):
        lister_props_dict = {}
        if self.details:
            lister_props_dict["details"] = self.details
        if self.fetch:
            lister_props_dict["fetch"] = self.fetch
        lister_props = replace(lister_default_props, **lister_props_dict)
        get_profile_list(lister_props)

    def switch_profile(self):
        switcher_props_dict = {}
        if self.profile:
            switcher_props_dict["profile"] = self.profile
        if self.fetch:
            switcher_props_dict["fetch"] = self.fetch
        switcher_props = replace(switcher_default_props, **switcher_props_dict)
        switch(switcher_props)

    def create_profile(self):
        creator_props_dict = {}
        if self.profile:
            creator_props_dict["profile"] = self.profile
        if self.fetch:
            creator_props_dict["fetch"] = self.fetch
        creator_props = replace(creator_default_props, **creator_props_dict)
        create(creator_props)

    def remove_profile(self):
        remover_props_dict = {}
        if self.profile:
            remover_props_dict["profile"] = self.profile
        if self.fetch:
            remover_props_dict["fetch"] = self.fetch
        if self.no_confirm:
            remover_props_dict["no_confirm"] = self.no_confirm
        remove_props = replace(remover_default_props, **remover_props_dict)
        remove(remove_props)

    def export_profile(self):
        exporter_props_dict = {}
        if self.skip_sudo:
            exporter_props_dict["skip_sudo"] = self.skip_sudo
        if self.password:
            exporter_props_dict["password"] = self.password
        if self.profile:
            exporter_props_dict["profile"] = self.profile
        exporter_props = replace(exporter_default_props, **exporter_props_dict)
        exporter(exporter_props)

    def import_profile(self):
        importer_props_dict = {}
        if self.skip_sudo:
            importer_props_dict["skip_sudo"] = self.skip_sudo
        if self.password:
            importer_props_dict["password"] = self.password
        if self.profile:
            importer_props_dict["profile"] = Path(self.profile)
        importer_props = replace(importer_default_props, **importer_props_dict)
        importer(importer_props)


@exception_handler
def main():
    parser = get_parser()
    args = parser.parse_args()

    if not args.action:
        parser.print_help()
        return

    try:
        action = Action(args.action)
    except ValueError:
        parser.error(f"Invalid action: {args.action}")

    if args.action == "init":
        dot_ctl_obj = DotCtl(
            action=action,
            git_url=args.url,
            profile=args.profile,
            config=args.config,
            env=args.env,
        )
        dot_ctl_obj.run()
    elif args.action == "save":
        dot_ctl_obj = DotCtl(
            action=action,
            skip_sudo=args.skip_sudo,
            password=args.password,
            profile=args.profile,
        )
        dot_ctl_obj.run()
    elif args.action == "apply":
        dot_ctl_obj = DotCtl(
            action=action,
            skip_sudo=args.skip_sudo,
            password=args.password,
            profile=args.profile,
        )
        dot_ctl_obj.run()
    elif args.action == "list":
        dot_ctl_obj = DotCtl(
            action=action,
            details=args.details,
            fetch=args.fetch,
        )
        dot_ctl_obj.run()
    elif args.action == "switch":
        dot_ctl_obj = DotCtl(
            action=action,
            profile=args.profile,
            fetch=args.fetch,
        )
        dot_ctl_obj.run()
    elif args.action == "create":
        dot_ctl_obj = DotCtl(
            action=action,
            profile=args.profile,
            fetch=args.fetch,
        )
        dot_ctl_obj.run()
    elif args.action == "remove":
        dot_ctl_obj = DotCtl(
            action=action,
            profile=args.profile,
            fetch=args.fetch,
            no_confirm=args.no_confirm,
        )
        dot_ctl_obj.run()
    elif args.action == "export":
        dot_ctl_obj = DotCtl(
            action=action,
            skip_sudo=args.skip_sudo,
            password=args.password,
            profile=args.profile,
        )
        dot_ctl_obj.run()
    elif args.action == "import":
        dot_ctl_obj = DotCtl(
            action=action,
            skip_sudo=args.skip_sudo,
            password=args.password,
            profile=args.profile,
        )
        dot_ctl_obj.run()


if __name__ == "__main__":
    main()
