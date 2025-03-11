from enum import Enum
from pathlib import Path
from dataclasses import replace
from .arg_manager import get_parser
from .exception import exception_handler
from .actions.Initializer import initialise, InitializerProps, initializer_default_props


class Action(Enum):
    init = "init"
    list = "list"
    switch = "switch"
    save = "save"
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
        *args,
        **kwargs,
    ):
        self.action = action
        self.git_url = git_url
        self.profile = profile
        self.config = config
        self.env = str(env) if env else None

    def run(self):
        if self.action == Action.init:
            self.init()

    def init(self):
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

    dot_ctl_obj = DotCtl(
        action=action,
        git_url=args.url,
        profile=args.profile,
        config=args.config,
        env=args.env,
    )
    dot_ctl_obj.run()


if __name__ == "__main__":
    main()
