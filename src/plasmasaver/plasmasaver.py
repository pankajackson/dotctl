import os
import re
import pwd
import time
from datetime import datetime
import shutil
import getpass
import subprocess
import traceback
from random import shuffle
from zipfile import is_zipfile, ZipFile
import argparse
import pkg_resources


try:
    import yaml
except ModuleNotFoundError as error:
    raise ModuleNotFoundError(
        "Please install the module PyYAML using pip: \n" "pip install PyYAML"
    ) from error

config_dir = '.config'
share_dir = '.local/share'
root_share_dir = '/usr/share'
bin_dir = '.local/bin'
base_plasmasaver_dir = '.plasmasaver'
base_profile_dir = 'profiles'
sddm_dir = '/usr/share/sddm'
system_config_dir = '/etc'
home_path = pwd.getpwuid(os.getuid()).pw_dir
config_dir_path = os.path.join(home_path, config_dir)
share_dir_path = os.path.join(home_path, share_dir)
bin_dir_path = os.path.join(home_path, bin_dir)
base_plasmasaver_dir_path = os.path.join(home_path, base_plasmasaver_dir)
base_profile_dir_path = os.path.join(base_plasmasaver_dir_path, base_profile_dir)
plasmasaver_config_file_path = os.path.join(base_plasmasaver_dir_path, 'conf.yaml')
temp_path = os.path.join(base_plasmasaver_dir_path, 'tmp-%s' % time.time())
EXPORT_EXTENSION = ".plsv"
sudo_pass = None
skip_sudo = False

if not os.path.exists(base_profile_dir_path):
    os.makedirs(base_profile_dir_path)

list_of_profiles = os.listdir(base_profile_dir_path)
length_of_lop = len(list_of_profiles)
version = pkg_resources.get_distribution('plasmasaver').version

conf_kde = {
    "export": {
        "home_folder": {
            "entries": [
                ".fonts",
                ".themes",
                ".icons",
                ".wallpapers",
                ".conky",
                ".zsh",
                ".bin",
                "bin"
            ],
            "location": "$HOME/"
        },
        "plasma_saver": {
            "entries": [
                "profiles"
            ],
            "location": "$PLASMA_SAVER_DIR"
        },
        "sddm": {
            "entries": [
                "themes"
            ],
            "location": "$SDDM_DIR"
        },
        "root_share_folder": {
            "entries": [
                "plasma",
                "kwin",
                "konsole",
                "fonts",
                "kfontinst",
                "color-schemes",
                "aurorae",
                "icons",
                "wallpapers",
                "Kvantum",
                "themes"
            ],
            "location": "$ROOT_SHARE_DIR"
        },
        "share_folder": {
            "entries": [
                "plasma",
                "kwin",
                "konsole",
                "fonts",
                "kfontinst",
                "color-schemes",
                "aurorae",
                "icons",
                "wallpapers"
            ],
            "location": "$SHARE_DIR"
        }
    },
    "save": {
        "home_folder": {
            "entries": [
                ".zshrc",
                ".p10k.zsh"
            ],
            "location": "$HOME/"
        },
        "app_layouts": {
            "entries": [
                "dolphin",
                "konsole"
            ],
            "location": "$HOME/.local/share/kxmlgui5"
        },
        "configs": {
            "entries": [
                "gtk-2.0",
                "gtk-3.0",
                "gtk-4.0",
                "Kvantum",
                "latte",
                "dolphinrc",
                "konsolerc",
                "kcminputrc",
                "kdeglobals",
                "kglobalshortcutsrc",
                "klipperrc",
                "krunnerrc",
                "kscreenlockerrc",
                "ksmserverrc",
                "kwinrc",
                "kwinrulesrc",
                "plasma-org.kde.plasma.desktop-appletsrc",
                "plasmarc",
                "plasmashellrc",
                "gtkrc",
                "gtkrc-2.0",
                "lattedockrc",
                "breezerc",
                "oxygenrc",
                "lightlyrc",
                "ksplashrc",
                "khotkeysrc",
                "autostart"
            ],
            "location": "$CONFIG_DIR"
        },
        "sddm_configs": {
            "entries": [
                "sddm.conf.d"
            ],
            "location": "$SYS_CONFIG_DIR"
        }
    }
}

conf_others = {
    "save": {
        "configs": {
            "location": "$HOME/.config",
            "entries": []
        }
    },
    "export": {
        "share_folder": {
            "location": "$HOME/.local/share",
            "entries": []
        },
        "home_folder": {
            "location": "$HOME/",
            "entries": []
        }
    }
}


def conf_initializer(env="NONE"):
    if not os.path.exists(plasmasaver_config_file_path) or (env and (env != "NONE")):
        if os.path.expandvars("$XDG_CURRENT_DESKTOP") == "KDE" or env.upper() == "KDE":
            conf = conf_kde
            with open(plasmasaver_config_file_path, 'w') as outfile:
                yaml.dump(conf, outfile, default_flow_style=False)
        else:
            print(
                f"plasmasaver: Unknown Desktop environment, please use \"-e\"/\"--env\" to specify environment with \"save\" command to initialize base config."
            )
            conf = conf_others
            with open(plasmasaver_config_file_path, 'w') as outfile:
                yaml.dump(conf, outfile, default_flow_style=False)
    return plasmasaver_config_file_path


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


def ends_with(grouped_regex, path) -> str:
    occurrence = re.search(grouped_regex, path).group()
    dirs = os.listdir(path[0: path.find(occurrence)])
    ends_with_text = re.search(grouped_regex, occurrence).group(2)
    for directory in dirs:
        if directory.endswith(ends_with_text):
            return path.replace(occurrence, directory)
    return occurrence


def begins_with(grouped_regex, path) -> str:
    occurrence = re.search(grouped_regex, path).group()
    dirs = os.listdir(path[0: path.find(occurrence)])
    ends_with_text = re.search(grouped_regex, occurrence).group(2)
    for directory in dirs:
        if directory.startswith(ends_with_text):
            return path.replace(occurrence, directory)
    return occurrence


def parse_keywords(tokens_, token_symbol, parsed):
    for item in parsed:
        for name in parsed[item]:
            for key, value in tokens_["keywords"]["dict"].items():
                word = token_symbol + key
                location = parsed[item][name]["location"]
                if word in location:
                    parsed[item][name]["location"] = location.replace(word, value)


def parse_functions(tokens_, token_symbol, parsed):
    functions = tokens_["functions"]
    raw_regex = f"\\{token_symbol}{functions['raw_regex']}"
    grouped_regex = f"\\{token_symbol}{functions['grouped_regex']}"

    for item in parsed:
        for name in parsed[item]:
            location = parsed[item][name]["location"]
            occurrences = re.findall(raw_regex, location)
            if not occurrences:
                continue
            for occurrence in occurrences:
                func = re.search(grouped_regex, occurrence).group(1)
                if func in functions["dict"]:
                    parsed[item][name]["location"] = functions["dict"][func](
                        grouped_regex, location
                    )


TOKEN_SYMBOL = "$"
tokens = {
    "keywords": {
        "dict": {
            "HOME": home_path,
            "CONFIG_DIR": config_dir_path,
            "SHARE_DIR": share_dir_path,
            "ROOT_SHARE_DIR": root_share_dir,
            "BIN_DIR": bin_dir_path,
            "PLASMA_SAVER_DIR": base_plasmasaver_dir,
            "SDDM_DIR": sddm_dir,
            "SYS_CONFIG_DIR": system_config_dir,
        }
    },
    "functions": {
        "raw_regex": r"\{\w+\=(?:\"|')\S+(?:\"|')\}",
        "grouped_regex": r"\{(\w+)\=(?:\"|')(\S+)(?:\"|')\}",
        "dict": {"ENDS_WITH": ends_with, "BEGINS_WITH": begins_with},
    },
}


def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def log(msg, *args, **kwargs):
    print(f"PlasmaSaver: {msg.capitalize()}", *args, **kwargs)


def get_sudo_pass(file, sudo_max_attempts=3):
    s_pass = None
    print('Required sudo to process %s' % str(file))
    print('Please select one option from list:')
    print('     1. Provide sudo Password and apply to recurrence')
    print('     2. Provide sudo Password and apply to current file')
    print('     3. Skip all')
    print('     4. Skip current file')
    sudo_behaviour_status = int(input("Please provide your input [1/2/3/4]: "))
    if sudo_behaviour_status == 1 or sudo_behaviour_status == 2:
        s_pass = getpass.getpass("Please provide password: ")
    if sudo_behaviour_status == 1:
        global sudo_pass
        sudo_pass = s_pass
        return s_pass
    elif sudo_behaviour_status == 2:
        return s_pass
    elif sudo_behaviour_status == 3:
        global skip_sudo
        skip_sudo = True
        return None
    elif sudo_behaviour_status == 4:
        return None
    else:
        log('Error: bad input')
        if sudo_max_attempts > 0:
            log('Error: Input limit exceed')
            return get_sudo_pass(file, sudo_max_attempts=sudo_max_attempts - 1)
        else:
            return None


@exception_handler
def copy(source, dest):
    assert isinstance(source, str) and isinstance(dest, str), "Invalid path"
    assert source != dest, "Source and destination can't be same"
    assert os.path.exists(source), "Source path doesn't exist"

    if not os.path.exists(dest):
        try:
            os.makedirs(dest)
        except PermissionError:
            command = 'mkdir -p %s' % dest
            if sudo_pass:
                subprocess.check_output('echo %s|sudo -S %s; echo $? ' % (sudo_pass, command), shell=True)
            elif skip_sudo:
                pass
            else:
                temp_pass = get_sudo_pass(dest)
                subprocess.check_output('echo %s|sudo -S %s; echo $? ' % (temp_pass, command), shell=True)

    for item in os.listdir(source):
        source_path = os.path.join(source, item)
        dest_path = os.path.join(dest, item)

        if os.path.isdir(source_path):
            copy(source_path, dest_path)
        else:
            if os.path.exists(dest_path):
                try:
                    os.remove(dest_path)
                except PermissionError:
                    command = 'rm -rf %s' % dest_path
                    if sudo_pass:
                        subprocess.check_output('echo %s|sudo -S %s; echo $? ' % (sudo_pass, command), shell=True)
                    elif skip_sudo:
                        pass
                    else:
                        temp_pass = get_sudo_pass(dest_path)
                        subprocess.check_output('echo %s|sudo -S %s; echo $? ' % (temp_pass, command), shell=True)

            if os.path.exists(source_path):
                try:
                    shutil.copy(source_path, dest)
                except PermissionError:
                    command = 'cp %s %s' % (source_path, dest)
                    if sudo_pass:
                        subprocess.check_output('echo %s|sudo -S %s; echo $? ' % (sudo_pass, command), shell=True)
                    elif skip_sudo:
                        pass
                    else:
                        temp_pass = get_sudo_pass(dest)
                        subprocess.check_output('echo %s|sudo -S %s; echo $? ' % (temp_pass, command), shell=True)


@exception_handler
def read_plasmasaver_config(config_file=plasmasaver_config_file_path) -> dict:
    with open(config_file, "r") as text:
        plasmasaver = yaml.load(text.read(), Loader=yaml.SafeLoader)
    parse_keywords(tokens, TOKEN_SYMBOL, plasmasaver)
    parse_functions(tokens, TOKEN_SYMBOL, plasmasaver)

    return plasmasaver


@exception_handler
def list_profiles(profile_list, profile_count):
    # assert
    assert os.path.exists(base_profile_dir_path) and profile_count != 0, "No profile found."

    # run
    print("Plasmasaver profiles:")
    print("ID\tNAME")
    for i, item in enumerate(profile_list):
        print(f"{i + 1}\t{item}")


@exception_handler
def save_profile(name, profile_list, force=False, include_global=False, include_sddm=False, sddm_only=False):
    # assert
    assert name not in profile_list or force, "Profile with this name already exists"

    # run
    log("saving profile...")
    profile_dir = os.path.join(base_profile_dir_path, name)
    mkdir(profile_dir)
    with open(plasmasaver_config_file_path, 'r') as configs:
        plasmasaver_config = yaml.safe_load(configs)
        if sddm_only:
            plasmasaver_config['export'] = {'sddm': plasmasaver_config['export']['sddm']}
            plasmasaver_config['save'] = {'sddm_configs': plasmasaver_config['save']['sddm_configs']}
        else:
            if not include_global:
                plasmasaver_config['export'].pop('root_share_folder', None)
            if not include_sddm:
                plasmasaver_config['export'].pop('sddm', None)
                plasmasaver_config['save'].pop('sddm_configs', None)

        with open(os.path.join(profile_dir, 'conf.yaml'), 'w') as outfile:
            yaml.dump(plasmasaver_config, outfile, default_flow_style=False)
    plasmasaver_config = read_plasmasaver_config(os.path.join(profile_dir, 'conf.yaml'))
    for section in plasmasaver_config['save']:
        location = plasmasaver_config['save'][section]["location"]
        folder = os.path.join(profile_dir, section)
        mkdir(folder)
        for entry in plasmasaver_config['save'][section]["entries"]:
            source = os.path.join(location, entry)
            dest = os.path.join(folder, entry)
            if os.path.exists(source):
                if os.path.isdir(source):
                    copy(source, dest)
                else:
                    shutil.copy(source, dest)

    log("Profile saved successfully!")


@exception_handler
def apply_profile(profile_name, profile_list, profile_count, skip_sddm=False, skip_global=False, sddm_only=False):
    # assert
    assert profile_count != 0, "No profile saved yet."
    assert profile_name in profile_list, "Profile not found :("

    # run
    profile_dir = os.path.join(base_profile_dir_path, profile_name)

    log("copying files...")

    config_location = os.path.join(profile_dir, "conf.yaml")
    profile_config = read_plasmasaver_config(config_location)
    if sddm_only:
        profile_config['export'] = {'sddm': profile_config['export']['sddm']}
        profile_config['save'] = {'sddm_configs': profile_config['save']['sddm_configs']}
    else:
        if skip_global:
            profile_config['export'].pop('root_share_folder', None)
        if skip_sddm:
            profile_config['export'].pop('sddm', None)
            profile_config['save'].pop('sddm_configs', None)
    for name in profile_config["save"]:
        location = os.path.join(profile_dir, name)
        copy(location, profile_config["save"][name]["location"])

    log(
        "Profile applied successfully! Please log-out and log-in to see the changes completely!"
    )


@exception_handler
def remove_profile(profile_name, profile_list, profile_count):
    # assert
    assert profile_count != 0, "No profile saved yet."
    assert profile_name in profile_list, "Profile not found."

    # run
    log("removing profile...")
    shutil.rmtree(os.path.join(base_profile_dir_path, profile_name))
    log("removed profile successfully")


@exception_handler
def export(profile_name, profile_list, profile_count, skip_global=False, skip_sddm=False, sddm_only=False,
           config_only=False, data_only=False):
    # assert
    assert profile_count != 0, "No profile saved yet."
    assert profile_name in profile_list, "Profile not found."

    # run
    profile_dir = os.path.join(base_profile_dir_path, profile_name)
    export_path = os.path.join(home_path, profile_name)

    if os.path.exists(export_path):
        rand_str = list("abcdefg12345")
        shuffle(rand_str)
        export_path = export_path + "".join(rand_str)
    mkdir(export_path)

    # compressing the files as zip
    log("Exporting profile. It might take a minute or two...")

    profile_config_file = os.path.join(profile_dir, "conf.yaml")
    with open(profile_config_file, 'r') as configs:
        plasmasaver_config = yaml.safe_load(configs)

        if skip_global:
            plasmasaver_config['export'].pop('root_share_folder', None)
        if data_only:
            plasmasaver_config.pop('save', None)
        if config_only:
            plasmasaver_config.pop('export', None)
        if skip_sddm:
            plasmasaver_config['export'].pop('sddm', None)
            plasmasaver_config['save'].pop('sddm_configs', None)
        if sddm_only:
            plasmasaver_config['export'] = {'sddm': plasmasaver_config['export']['sddm']}
            plasmasaver_config['save'] = {'sddm_configs': plasmasaver_config['save']['sddm_configs']}

        with open(os.path.join(export_path, "conf.yaml"), 'w') as outfile:
            yaml.dump(plasmasaver_config, outfile, default_flow_style=False)

    plasmasaver_config = read_plasmasaver_config(os.path.join(export_path, "conf.yaml"))

    export_path_save = mkdir(os.path.join(export_path, "save"))
    for name in plasmasaver_config["save"]:
        location = os.path.join(profile_dir, name)
        log(f'Exporting "{name}"...')
        copy(location, os.path.join(export_path_save, name))

    plasmasaver_config_export = plasmasaver_config["export"]
    export_path_export = mkdir(os.path.join(export_path, "export"))
    for name in plasmasaver_config_export:
        location = plasmasaver_config_export[name]["location"]
        path = mkdir(os.path.join(export_path_export, name))
        for entry in plasmasaver_config_export[name]["entries"]:
            source = os.path.join(location, entry)
            dest = os.path.join(path, entry)
            log(f'Exporting "{name}/{entry}"...')
            if os.path.exists(source):
                if os.path.isdir(source):
                    copy(source, dest)
                else:
                    shutil.copy(source, dest)

    log("Creating archive")
    shutil.make_archive(export_path, "zip", export_path)

    shutil.rmtree(export_path)
    shutil.move(export_path + ".zip", export_path + EXPORT_EXTENSION)

    log(f"Successfully exported to {export_path}{EXPORT_EXTENSION}")


@exception_handler
def import_profile(path, skip_global=False, skip_sddm=False, sddm_only=False, config_only=False, data_only=False):
    # assert
    assert (
            is_zipfile(path) and path[-5:] == EXPORT_EXTENSION
    ), "Not a valid plasmasaver file"
    item = os.path.basename(path)[:-5]
    assert not os.path.exists(
        os.path.join(base_profile_dir_path, item)
    ), "A profile with this name already exists"

    # run
    log("Importing profile. It might take a minute or two...")

    item = os.path.basename(path).replace(EXPORT_EXTENSION, "")

    with ZipFile(path, "r") as zip_file:
        zip_file.extractall(temp_path)

    config_file_location = os.path.join(temp_path, "conf.yaml")
    plasmasaver_config = read_plasmasaver_config(config_file_location)

    if skip_global:
        plasmasaver_config['export'].pop('root_share_folder', None)
    if data_only:
        plasmasaver_config.pop('save', None)
    if config_only:
        plasmasaver_config.pop('export', None)
    if skip_sddm:
        plasmasaver_config['export'].pop('sddm', None)
        plasmasaver_config['save'].pop('sddm_configs', None)
    if sddm_only:
        plasmasaver_config['export'] = {'sddm': plasmasaver_config['export']['sddm']}
        plasmasaver_config['save'] = {'sddm_configs': plasmasaver_config['save']['sddm_configs']}

    profile_dir = os.path.join(base_profile_dir_path, item)
    copy(os.path.join(temp_path, "save"), profile_dir)
    shutil.copy(os.path.join(temp_path, "conf.yaml"), profile_dir)

    for section in plasmasaver_config["export"]:
        location = plasmasaver_config["export"][section]["location"]
        path = os.path.join(temp_path, "export", section)
        mkdir(path)
        for entry in plasmasaver_config["export"][section]["entries"]:
            source = os.path.join(path, entry)
            dest = os.path.join(location, entry)
            log(f'Importing "{section}/{entry}"...')
            if os.path.exists(source):
                if os.path.isdir(source):
                    copy(source, dest)
                else:
                    try:
                        shutil.copy(source, dest)
                    except PermissionError:
                        command = 'cp %s %s' % (source, dest)
                        if sudo_pass:
                            subprocess.check_output('echo %s|sudo -S %s; echo $? ' % (sudo_pass, command), shell=True)
                        elif skip_sudo:
                            pass
                        else:
                            temp_pass = get_sudo_pass(dest)
                            subprocess.check_output('echo %s|sudo -S %s; echo $? ' % (temp_pass, command), shell=True)

    shutil.rmtree(temp_path)

    log("Profile successfully imported!")


@exception_handler
def wipe():
    """Wipes all profiles."""
    confirm = input('This will wipe all your profiles. Enter "WIPE" Tto continue: ')
    if confirm == "WIPE":
        shutil.rmtree(base_profile_dir_path)
        log("Removed all profiles!")
    else:
        log("Aborting...")


def _get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="plasmasaver",
        epilog="Please report bugs at pankajackson@live.co.uk",
    )

    parser.add_argument(
        "-v", "--version", required=False, action="store_true", help="Show version"
    )

    subparsers = parser.add_subparsers(help='Desired action to perform', dest='action')
    save_parser = subparsers.add_parser("save", help="Save current config as a profile")
    remove_parser = subparsers.add_parser("remove", help="Remove the specified profile")
    list_parser = subparsers.add_parser("list", help="Lists created profiles")
    apply_parser = subparsers.add_parser("apply", help="Apply the specified profile")
    import_parser = subparsers.add_parser("import", help="Import a plasmasaver file")
    export_parser = subparsers.add_parser("export", help="Export a profile and share with your friends!")
    wipe_parser = subparsers.add_parser("wipe", help="Wipes all profiles.")

    save_parser.add_argument(
        "profile_name",
        type=str,
        help="Name of the profile as a identifier"
    )
    save_parser.add_argument(
        "-f",
        "--force",
        required=False,
        action="store_true",
        help="Overwrite already saved profiles",
    )
    save_parser.add_argument(
        "-c",
        "--config-file",
        required=False,
        type=str,
        help="Use external config file",
        metavar="<path>",
    )
    save_parser.add_argument(
        "-e",
        "--env",
        required=False,
        type=str,
        help="Desktop environment (e.g. kde)",
        metavar="<env>",
    )
    save_parser.add_argument(
        "-p",
        "--password",
        required=False,
        type=str,
        help="Sudo Password to authorize restricted data (e.g. /usr/share)",
        metavar="<password>",
    )
    save_parser.add_argument(
        "--include-global",
        required=False,
        action="store_true",
        help="Include data from global data directory (/usr/share)",
    )
    save_parser.add_argument(
        "--include-sddm",
        required=False,
        action="store_true",
        help="Include sddm data/configs directory (/usr/share/sddm, /etc/sddm.conf.d)",
    )
    save_parser.add_argument(
        "--sddm-only",
        required=False,
        action="store_true",
        help="Perform operation only on sddm data/configurations (Note: sudo password required)",
    )
    save_parser.add_argument(
        "--skip-sudo",
        required=False,
        action="store_true",
        help="Skip all sudo operations",
    )
    remove_parser.add_argument(
        "profile_name",
        type=str,
        help="Name of the profile as a identifier"
    )
    apply_parser.add_argument(
        "profile_name",
        type=str,
        help="Name of the profile as a identifier"
    )
    apply_parser.add_argument(
        "-p",
        "--password",
        required=False,
        type=str,
        help="Sudo Password to authorize restricted data (e.g. /usr/share)",
        metavar="<password>",
    )
    apply_parser.add_argument(
        "--sddm-only",
        required=False,
        action="store_true",
        help="Perform operation only on sddm data/configurations (Note: sudo password required)",
    )
    apply_parser.add_argument(
        "--skip-global",
        required=False,
        action="store_true",
        help="Skip data from global data directory (/usr/share)",
    )
    apply_parser.add_argument(
        "--skip-sddm",
        required=False,
        action="store_true",
        help="Skip sddm data/configs directory (/usr/share/sddm, /etc/sddm.conf.d)",
    )
    apply_parser.add_argument(
        "--skip-sudo",
        required=False,
        action="store_true",
        help="Skip all sudo operations",
    )
    export_parser.add_argument(
        "profile_name",
        type=str,
        help="Name of the profile as a identifier"
    )
    export_parser.add_argument(
        "-p",
        "--password",
        required=False,
        type=str,
        help="Sudo Password to authorize restricted data (e.g. /usr/share)",
        metavar="<password>",
    )
    export_parser.add_argument(
        "--config-only",
        required=False,
        action="store_true",
        help="Perform operation only on plasma configs (skip data, e.g. ~/.config)",
    )
    export_parser.add_argument(
        "--data-only",
        required=False,
        action="store_true",
        help="Perform operation only on plasma data (skip configs, e.g. ~/.local/share)",
    )
    export_parser.add_argument(
        "--sddm-only",
        required=False,
        action="store_true",
        help="Perform operation only on sddm data/configurations (Note: sudo password required)",
    )
    export_parser.add_argument(
        "--skip-global",
        required=False,
        action="store_true",
        help="Skip data from global data directory (/usr/share)",
    )
    export_parser.add_argument(
        "--skip-sddm",
        required=False,
        action="store_true",
        help="Skip sddm data/configs directory (/usr/share/sddm, /etc/sddm.conf.d)",
    )
    export_parser.add_argument(
        "--skip-sudo",
        required=False,
        action="store_true",
        help="Skip all sudo operations",
    )
    import_parser.add_argument(
        "profile_name",
        type=str,
        help="Name of the profile as a identifier"
    )
    import_parser.add_argument(
        "-p",
        "--password",
        required=False,
        type=str,
        help="Sudo Password to authorize restricted data (e.g. /usr/share)",
        metavar="<password>",
    )
    import_parser.add_argument(
        "--config-only",
        required=False,
        action="store_true",
        help="Perform operation only on plasma configs (skip data, e.g. ~/.config)",
    )
    import_parser.add_argument(
        "--data-only",
        required=False,
        action="store_true",
        help="Perform operation only on plasma data (skip configs, e.g. ~/.local/share)",
    )
    import_parser.add_argument(
        "--sddm-only",
        required=False,
        action="store_true",
        help="Perform operation only on sddm data/configurations (Note: sudo password required)",
    )
    import_parser.add_argument(
        "--skip-global",
        required=False,
        action="store_true",
        help="Skip data from global data directory (/usr/share)",
    )
    import_parser.add_argument(
        "--skip-sddm",
        required=False,
        action="store_true",
        help="Skip sddm data/configs directory (/usr/share/sddm, /etc/sddm.conf.d)",
    )
    import_parser.add_argument(
        "--skip-sudo",
        required=False,
        action="store_true",
        help="Skip all sudo operations",
    )

    return parser


@exception_handler
def main():
    """The main function that handles all the arguments and options."""

    parser = _get_parser()
    args = parser.parse_args()
    global skip_sudo
    skip_sudo = False
    global sudo_pass
    sudo_pass = None
    conf_initializer()

    if args.action == 'save':
        if args.password and args.skip_sudo:
            raise Exception('error: -p/--password and --skip-sudo can\'t be used at the same time')
        elif args.skip_sudo:
            skip_sudo = True
        elif args.password:
            sudo_pass = args.password
        if (args.sddm_only and args.include_sddm) or (args.sddm_only and args.include_global):
            raise Exception('error: --sddm-only can\'t be used with --include-sddm and --include-global')
        if args.env:
            conf_initializer(args.env)
        if args.config_file:
            if not os.path.exists(args.config_file):
                raise Exception(
                    'error: invalid config file path, The path given in arg doesn\'t exist or is not accessible: %s' % args.config_file)
            with open(args.config_file, 'r') as configs:
                e_conf = yaml.safe_load(configs)
                if 'export' not in e_conf.keys() or 'save' not in e_conf.keys():
                    raise Exception(
                        'error: missing config block(s), "save" and "export" are core blocks of plasmasaver configuration')
            if e_conf:
                global plasmasaver_config_file_path
                plasmasaver_config_file_path = args.config_file
        save_profile(args.profile_name, list_of_profiles, force=args.force, include_sddm=args.include_sddm,
                     include_global=args.include_global, sddm_only=args.sddm_only)
    elif args.action == 'remove':
        remove_profile(args.profile_name, list_of_profiles, length_of_lop)

    elif args.action == 'list':
        list_profiles(list_of_profiles, length_of_lop)

    elif args.action == 'apply':
        if args.password and args.skip_sudo:
            raise Exception('error: -p/--password and --skip-sudo can\'t be used at the same time')
        elif args.skip_sudo:
            skip_sudo = True
        elif args.password:
            sudo_pass = args.password
        if (args.sddm_only and args.skip_sddm) or (args.sddm_only and args.skip_global):
            raise Exception('error: --sddm-only can\'t be used with --include-sddm and --include-global')
        apply_profile(args.profile_name, list_of_profiles, length_of_lop, skip_sddm=args.skip_sddm,
                      skip_global=args.skip_global, sddm_only=args.sddm_only)

    elif args.action == 'import':
        if args.password and args.skip_sudo:
            raise Exception('error: -p/--password and --skip-sudo can\'t be used at the same time')
        elif args.skip_sudo:
            skip_sudo = True
        elif args.password:
            sudo_pass = args.password
        if (args.sddm_only and args.skip_sddm) or (args.sddm_only and args.skip_global):
            raise Exception('error: --sddm-only can\'t be used with --include-sddm and --include-global')
        if args.data_only and args.config_only:
            raise Exception('error: --data-only and --config-only can\'t be used at the same time')
        import_profile(args.profile_name, skip_global=args.skip_global, skip_sddm=args.skip_sddm,
                       sddm_only=args.sddm_only, config_only=args.config_only, data_only=args.data_only)

    elif args.action == 'export':
        if args.password and args.skip_sudo:
            raise Exception('error: -p/--password and --skip-sudo can\'t be used at the same time')
        elif args.skip_sudo:
            skip_sudo = True
        elif args.password:
            sudo_pass = args.password
        if (args.sddm_only and args.skip_sddm) or (args.sddm_only and args.skip_global):
            raise Exception('error: --sddm-only can\'t be used with --include-sddm and --include-global')
        if args.data_only and args.config_only:
            raise Exception('error: --data-only and --config-only can\'t be used at the same time')
        export(args.profile_name, list_of_profiles, length_of_lop, skip_global=args.skip_global,
               skip_sddm=args.skip_sddm, sddm_only=args.sddm_only, config_only=args.config_only,
               data_only=args.data_only)

    elif args.version:
        print(f"plasmasaver: {version}")

    elif args.action == 'wipe':
        wipe()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
