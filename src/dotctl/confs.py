import os
import yaml
import re
from dotctl.exception import exception_handler
from dotctl.paths import (
    home_path,
    config_dir_path,
    share_dir_path,
    root_share_dir,
    bin_dir_path,
    sddm_dir,
    system_config_dir,
    base_plasmasaver_dir,
    base_profile_dir_path,
    plasmasaver_config_file_path,
)

EXPORT_EXTENSION = ".plsv"
sudo_pass = None
skip_sudo = False


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
                "bin",
            ],
            "location": "$HOME/",
        },
        "plasma_saver": {"entries": ["profiles"], "location": "$PLASMA_SAVER_DIR"},
        "sddm": {"entries": ["themes"], "location": "$SDDM_DIR"},
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
                "themes",
            ],
            "location": "$ROOT_SHARE_DIR",
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
                "wallpapers",
            ],
            "location": "$SHARE_DIR",
        },
    },
    "save": {
        "home_folder": {"entries": [".zshrc", ".p10k.zsh"], "location": "$HOME/"},
        "app_layouts": {
            "entries": ["dolphin", "konsole"],
            "location": "$HOME/.local/share/kxmlgui5",
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
                "autostart",
            ],
            "location": "$CONFIG_DIR",
        },
        "sddm_configs": {"entries": ["sddm.conf.d"], "location": "$SYS_CONFIG_DIR"},
    },
}

conf_others = {
    "save": {"configs": {"location": "$HOME/.config", "entries": []}},
    "export": {
        "share_folder": {"location": "$HOME/.local/share", "entries": []},
        "home_folder": {"location": "$HOME/", "entries": []},
    },
}


def ends_with(grouped_regex, path) -> str:
    occurrence = re.search(grouped_regex, path).group()
    dirs = os.listdir(path[0 : path.find(occurrence)])
    ends_with_text = re.search(grouped_regex, occurrence).group(2)
    for directory in dirs:
        if directory.endswith(ends_with_text):
            return path.replace(occurrence, directory)
    return occurrence


def begins_with(grouped_regex, path) -> str:
    occurrence = re.search(grouped_regex, path).group()
    dirs = os.listdir(path[0 : path.find(occurrence)])
    ends_with_text = re.search(grouped_regex, occurrence).group(2)
    for directory in dirs:
        if directory.startswith(ends_with_text):
            return path.replace(occurrence, directory)
    return occurrence


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
    }
}


def parse_keywords(tokens_, token_symbol, parsed):
    for item in parsed:
        for name in parsed[item]:
            for key, value in tokens_["keywords"]["dict"].items():
                word = token_symbol + key
                location = parsed[item][name]["location"]
                if word in location:
                    parsed[item][name]["location"] = location.replace(word, value)


@exception_handler
def read_plasmasaver_config(config_file=plasmasaver_config_file_path) -> dict:
    with open(config_file, "r") as text:
        plasmasaver = yaml.load(text.read(), Loader=yaml.SafeLoader)
    parse_keywords(tokens, TOKEN_SYMBOL, plasmasaver)

    return plasmasaver


def conf_initializer(env="NONE"):
    if not os.path.exists(plasmasaver_config_file_path) or (env and (env != "NONE")):
        if os.path.expandvars("$XDG_CURRENT_DESKTOP") == "KDE" or env.upper() == "KDE":
            conf = conf_kde
            with open(plasmasaver_config_file_path, "w") as outfile:
                yaml.dump(conf, outfile, default_flow_style=False)
        else:
            print(
                f'plasmasaver: Unknown Desktop environment, please use "-e"/"--env" to specify environment with "save" command to initialize base config.'
            )
            conf = conf_others
            with open(plasmasaver_config_file_path, "w") as outfile:
                yaml.dump(conf, outfile, default_flow_style=False)
    return plasmasaver_config_file_path
