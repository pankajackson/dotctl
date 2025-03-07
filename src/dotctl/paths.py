import os
import pwd
import time


config_dir = ".config"
share_dir = ".local/share"
root_share_dir = "/usr/share"
bin_dir = ".local/bin"
base_plasmasaver_dir = ".plasmasaver"
base_profile_dir = "profiles"
sddm_dir = "/usr/share/sddm"
system_config_dir = "/etc"
home_path = pwd.getpwuid(os.getuid()).pw_dir
config_dir_path = os.path.join(home_path, config_dir)
share_dir_path = os.path.join(home_path, share_dir)
bin_dir_path = os.path.join(home_path, bin_dir)
base_plasmasaver_dir_path = os.path.join(home_path, base_plasmasaver_dir)
base_profile_dir_path = os.path.join(base_plasmasaver_dir_path, base_profile_dir)
plasmasaver_config_file_path = os.path.join(base_plasmasaver_dir_path, "conf.yaml")
temp_path = os.path.join(base_plasmasaver_dir_path, "tmp-%s" % time.time())
