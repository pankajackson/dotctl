from dotctl import __APP_NAME__


def log(msg, *args, **kwargs):
    print(f"{__APP_NAME__}: {msg.capitalize()}", *args, **kwargs)
