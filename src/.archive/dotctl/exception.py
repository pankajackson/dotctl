import os
import pwd
import traceback
from datetime import datetime
from .paths import home_path


def exception_handler(func):
    def inner_func(*args, **kwargs):
        try:
            function = func(*args, **kwargs)
        except Exception as err:
            dateandtime = datetime.now().strftime("[%d/%m/%Y %H:%M:%S]")
            log_file = os.path.join(home_path, "plasmasaver_log.txt")

            with open(log_file, "a") as file:
                file.write(dateandtime + "\n")
                traceback.print_exc(file=file)
                file.write("\n")

            print(
                f"plasmasaver: {err}\nPlease check the log at {log_file} for more details."
            )
            return None
        else:
            return function

    return inner_func
