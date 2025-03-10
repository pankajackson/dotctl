from .arg_manager import get_parser
from .exception import exception_handler


class DotCtl:
    def __init__(self):
        pass


@exception_handler
def main():

    parser = get_parser()
    args = parser.parse_args()


if __name__ == "__main__":
    main()
