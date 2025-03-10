import os
import traceback
from datetime import datetime
from dotctl_alpha.paths import app_home_directory
from dotctl_alpha import __APP_NAME__


def exception_handler(func):
    def inner_func(*args, **kwargs):
        try:
            function = func(*args, **kwargs)
        except Exception as err:
            dateandtime = datetime.now().strftime("[%d/%m/%Y %H:%M:%S]")
            log_file = os.path.join(app_home_directory, f"{__APP_NAME__}.log")

            with open(log_file, "a") as file:
                file.write(dateandtime + "\n")
                traceback.print_exc(file=file)
                file.write("\n")

            print(
                f"{__APP_NAME__}: {err}\nPlease check the log at {log_file} for more details."
            )
            return None
        else:
            return function

    return inner_func
