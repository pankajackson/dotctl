import os
import pwd
from dotctl import __APP_NAME__


home_path = pwd.getpwuid(os.getuid()).pw_dir
app_home_directory = os.path.join(home_path, __APP_NAME__)
profile_directory = os.path.join(app_home_directory, "profiles")
