import sys
from dotctl import __APP_NAME__


def new_line():
    sys.stdout.write("\n")
    sys.stdout.flush()


def log(msg, *args, **kwargs):
    prefix = f"{__APP_NAME__}: "
    cleaned_msg = msg.removeprefix(prefix).capitalize()
    print(f"{prefix}{cleaned_msg}", *args, **kwargs)
