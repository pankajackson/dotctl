import os
import pwd
import time
from dotctl import __APP_NAME__


home_path = pwd.getpwuid(os.getuid()).pw_dir
app_home_directory = os.path.join(home_path, f".{__APP_NAME__}")
app_profile_directory = os.path.join(app_home_directory, "dots")
app_config_file = os.path.join(app_profile_directory, f"{__APP_NAME__}.yaml")
app_hooks_directory = os.path.join(app_profile_directory, "hooks")
temp_path = os.path.join(app_home_directory, "tmp-%s" % time.time())

config_directory = os.path.join(home_path, ".config")
local_directory = os.path.join(home_path, ".local")
share_directory = os.path.join(local_directory, "share")
bin_directory = os.path.join(local_directory, "bin")
sys_config_directory = "/etc"
sys_share_directory = "/usr/share"
