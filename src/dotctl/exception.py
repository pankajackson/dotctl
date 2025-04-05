import os
import traceback
import shutil
from pathlib import Path
from datetime import datetime
from dotctl.paths import app_home_directory
from dotctl import __APP_NAME__, __COMMANDS_REQ__
from .utils import log


def exception_handler(func):
    def inner_func(*args, **kwargs):
        try:
            function = func(*args, **kwargs)
        except Exception as err:
            dateandtime = datetime.now().strftime("[%d/%m/%Y %H:%M:%S]")
            log_file = Path(os.path.join(app_home_directory, f"{__APP_NAME__}.log"))
            if not log_file.parent.exists():
                log_file.parent.mkdir(parents=True, exist_ok=True)

            with open(log_file, "a") as file:
                file.write(dateandtime + "\n")
                traceback.print_exc(file=file)
                file.write("\n")

            log(
                f"{__APP_NAME__}: {err}\nPlease check the log at {log_file} for more details."
            )
            return None
        else:
            return function

    return inner_func


def check_req_commands(cmd_list: list[str] = __COMMANDS_REQ__):
    required_cmd_list = []
    for cmd in cmd_list:
        if not shutil.which(cmd):
            required_cmd_list.append(cmd)
    if required_cmd_list:
        raise Exception(f"Required commands not found: {required_cmd_list}")
