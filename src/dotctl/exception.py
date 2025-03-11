import os
import traceback
from pathlib import Path
from datetime import datetime
from dotctl.paths import app_home_directory
from dotctl import __APP_NAME__
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
