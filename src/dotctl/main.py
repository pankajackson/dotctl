from enum import Enum
from pathlib import Path
from dataclasses import replace
from dotctl import __APP_NAME__, __APP_VERSION__
from .arg_manager import get_parser
from .exception import exception_handler, check_req_commands
from .actions.initializer import initialise, initializer_default_props
from .actions.saver import save, saver_default_props
from .actions.activator import apply, activator_default_props
from .actions.lister import get_profile_list, lister_default_props
from .actions.switcher import switch, switcher_default_props
from .actions.creator import create, creator_default_props
from .actions.remover import remove, remover_default_props
from .actions.exporter import exporter, exporter_default_props
from .actions.importer import importer, importer_default_props
from .actions.wiper import wipe, wiper_default_props


class Action(Enum):
    INIT = "init"
    LIST = "list"
    LS = "ls"
    SWITCH = "switch"
    SW = "sw"
    SAVE = "save"
    APPLY = "apply"
    CREATE = "create"
    NEW = "new"
    REMOVE = "remove"
    RM = "rm"
    DELETE = "delete"
    DEL = "del"
    IMPORT = "import"
    EXPORT = "export"
    WIPE = "wipe"
    HELP = "help"
    VERSION = "version"


class DotCtl:
    def __init__(self, action: Action, **kwargs):
        self.action = action
        self.k_args: dict = kwargs

    def run(self):
        """Run the appropriate action based on the provided command."""
        action_methods = {
            Action.INIT: self.init_profile,
            Action.SAVE: self.save_dots,
            Action.APPLY: self.apply_dots,
            Action.LIST: self.list_profiles,
            Action.LS: self.list_profiles,
            Action.SWITCH: self.switch_profile,
            Action.SW: self.switch_profile,
            Action.CREATE: self.create_profile,
            Action.NEW: self.create_profile,
            Action.REMOVE: self.remove_profile,
            Action.RM: self.remove_profile,
            Action.DELETE: self.remove_profile,
            Action.DEL: self.remove_profile,
            Action.EXPORT: self.export_profile,
            Action.IMPORT: self.import_profile,
            Action.WIPE: self.wipe_profile,
        }
        action_methods.get(self.action, lambda: None)()

    def _build_props(self, defaults, *keys):
        """Utility function to build properties dictionary dynamically."""
        props = {k: v for k in keys if (v := self.k_args.get(k, None)) is not None}
        return replace(defaults, **props)

    def init_profile(self):
        """Initialize a new dotfiles profile."""
        props = self._build_props(
            initializer_default_props, "git_url", "profile", "config", "env"
        )
        initialise(props)

    def save_dots(self):
        """Save current dotfiles."""
        props = self._build_props(
            saver_default_props, "skip_sudo", "password", "profile"
        )
        save(props)

    def apply_dots(self):
        """Apply a saved dotfiles profile."""
        props = self._build_props(
            activator_default_props,
            "skip_sudo",
            "password",
            "profile",
            "skip_hooks",
            "skip_pre_hooks",
            "skip_post_hooks",
            "ignore_hook_errors",
        )
        apply(props)

    def list_profiles(self):
        """List available dotfiles profiles."""
        props = self._build_props(lister_default_props, "details", "fetch")
        get_profile_list(props)

    def switch_profile(self):
        """Switch to a different dotfiles profile."""
        props = self._build_props(switcher_default_props, "profile", "fetch")
        switch(props)

    def create_profile(self):
        """Create a new dotfiles profile."""
        props = self._build_props(creator_default_props, "profile", "fetch")
        create(props)

    def remove_profile(self):
        """Remove an existing dotfiles profile."""
        props = self._build_props(
            remover_default_props, "profile", "fetch", "no_confirm"
        )
        remove(props)

    def export_profile(self):
        """Export dotfiles profile."""
        props = self._build_props(
            exporter_default_props, "skip_sudo", "password", "profile"
        )
        exporter(props)

    def import_profile(self):
        """Import a dotfiles profile."""
        props = self._build_props(
            importer_default_props, "skip_sudo", "password", "profile"
        )
        importer(props)

    def wipe_profile(self):
        """Wipe dotfiles profile."""
        props = self._build_props(wiper_default_props, "no_confirm")
        wipe(props)


@exception_handler
def main():
    parser = get_parser()
    args = parser.parse_args()

    if args.version:
        print(f"{__APP_NAME__}: {__APP_VERSION__}")
        return

    if not args.action:
        parser.print_help()
        return

    check_req_commands()

    try:
        action = Action(args.action.lower())
    except ValueError:
        parser.error(f"Invalid action: {args.action}. Use '--help' for usage.")

    # Convert arguments to dictionary dynamically
    common_args = {
        "action": action,
        "git_url": getattr(args, "url", None),
        "profile": getattr(args, "profile", None),
        "config": getattr(args, "config", None),
        "env": getattr(args, "env", None),
        "skip_sudo": getattr(args, "skip_sudo", False),
        "skip_hooks": getattr(args, "skip_hooks", False),
        "skip_pre_hooks": getattr(args, "skip_pre_hooks", False),
        "skip_post_hooks": getattr(args, "skip_post_hooks", False),
        "ignore_hook_errors": getattr(args, "ignore_hook_errors", False),
        "password": getattr(args, "password", None),
        "details": getattr(args, "details", False),
        "fetch": getattr(args, "fetch", False),
        "no_confirm": getattr(args, "no_confirm", False),
    }

    dot_ctl_obj = DotCtl(**common_args)
    dot_ctl_obj.run()


if __name__ == "__main__":
    main()
