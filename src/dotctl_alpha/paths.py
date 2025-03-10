import os
import pwd
import time
from dotctl_alpha import __APP_NAME__


home_path = pwd.getpwuid(os.getuid()).pw_dir
app_home_directory = os.path.join(home_path, __APP_NAME__)
