from dotctl import __APP_NAME__


def log(msg, *args, **kwargs):
    prefix = f"{__APP_NAME__}: "
    cleaned_msg = msg.removeprefix(prefix).capitalize()
    print(f"{prefix}{cleaned_msg}", *args, **kwargs)
