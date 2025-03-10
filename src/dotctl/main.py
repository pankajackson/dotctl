from enum import Enum
from .arg_manager import get_parser
from .exception import exception_handler
from .handlers.Initializer import initialise


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
        *args,
        **kwargs,
    ):
        self.action = action
        self.git_url = git_url
        self.profile = profile

    def run(self):
        if self.action == Action.init:
            self.init()

    def init(self):
        initialise(self.git_url, self.profile)


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

    dot_ctl_obj = DotCtl(action, git_url=args.url, profile=args.profile)
    dot_ctl_obj.run()


if __name__ == "__main__":
    main()
