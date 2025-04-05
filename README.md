# DotCtl

**dotctl** is a powerful CLI tool to manage, save, apply, export, and import system configurations as named profiles.  
It helps centralize dotfiles and service configurations in Git repositories for seamless replication across systems.

Designed for developers and sysadmins, it supports pre/post hook scripts and is ideal for setting up consistent environments across desktops and servers.

---

## 📚 Table of Contents

- [DotCtl](#dotctl)
  - [📚 Table of Contents](#-table-of-contents)
  - [🚀 Features](#-features)
  - [🔧 Installation](#-installation)
  - [📘 Usage](#-usage)
  - [🛠️ Commands](#️-commands)
    - [📁 `init`](#-init)
    - [💾 `save`](#-save)
    - [📋 `list` / `ls`](#-list--ls)
    - [🔀 `switch` / `sw`](#-switch--sw)
    - [🆕 `create` / `new`](#-create--new)
    - [❌ `remove` / `rm` / `delete` / `del`](#-remove--rm--delete--del)
    - [🧪 `apply`](#-apply)
    - [📤 `export`](#-export)
    - [📥 `import`](#-import)
    - [🔥 `wipe`](#-wipe)
  - [🧑‍💻 Development \& Publishing](#-development--publishing)
    - [Setup Development Environment](#setup-development-environment)
    - [Build the Package](#build-the-package)
    - [Publish to TestPyPI](#publish-to-testpypi)
    - [Publish to PyPI](#publish-to-pypi)
  - [🙋 Contact](#-contact)

---

## 🚀 Features

- 📦 **Profile Management** — Create, switch, save, remove, and apply system profiles.
- 🌀 **Pre/Post Hooks** — Run scripts before or after activating a profile (e.g., install packages, restart services).
- 🔄 **Git Integration** — Sync profiles with local or remote Git repositories.
- 📁 **Portable Configs** — Export/import profiles using `.dtsv` files for easy backups and sharing.
- ⚙️ **Custom Configs** — Define tracking rules via `dotctl.yaml`.

---

## 🔧 Installation

```sh
pip install dotctl
```

---

## 📘 Usage

```sh
dotctl [OPTIONS] <COMMAND> [ARGS]
```

Run `dotctl -h` for global help or `dotctl <COMMAND> -h` for command-specific help.

---

## 🛠️ Commands

### 📁 `init`

Initialize a new profile.

```sh
dotctl init [-h] [-u <git-url>] [-p <profile>] [-c <config-path>] [-e <env>]
```

**Examples:**

```sh
dotctl init -e kde
dotctl init -u https://github.com/user880/dots.git -p mydesktop
dotctl init -c ./my_custom_config.yaml
```

**Options:**

- `-e, --env` – Target environment (e.g., kde, gnome, server).
- `-u, --url` – Git URL to clone profile from.
- `-p, --profile` – Activate this profile after init.
- `-c, --config` – Path to custom YAML config.

---

### 💾 `save`

Save current system state to the active profile.

```sh
dotctl save [-h] [-p <password>] [--skip-sudo] [profile]
```

**Examples:**

```sh
dotctl save
dotctl save my_web_server --skip-sudo
dotctl save my_web_server -p mYsecretp@ssw0rd
```

**Options:**

- `--skip-sudo` – Ignore restricted resources.
- `-p, --password` – Password for restricted resources.

---

### 📋 `list` / `ls`

List all profiles.

```sh
dotctl list [-h] [--details] [--fetch]
```

**Examples:**

```sh
dotctl list
dotctl list --details
dotctl list --fetch
```

**Options:**

- `--details` – Show extended info.
- `--fetch` – Refresh remote data.

---

### 🔀 `switch` / `sw`

Switch to another profile.

```sh
dotctl switch [-h] [--fetch] [profile]
```

**Examples:**

```sh
dotctl switch MyProfile
dotctl sw MyProfile --fetch
```

**Options:**

- `--fetch` – Refresh profile info before switching.

---

### 🆕 `create` / `new`

Create a new, empty profile.

```sh
dotctl create [-h] [--fetch] <profile>
```

**Examples:**

```sh
dotctl create myserver
dotctl new myserver --fetch
```

**Options:**

- `--fetch` – Sync with remote before creating.

---

### ❌ `remove` / `rm` / `delete` / `del`

Remove a profile locally and/or remotely.

```sh
dotctl remove [-h] [-y] [--fetch] <profile>
```

**Examples:**

```sh
dotctl rm MyProfile
dotctl del MyProfile --fetch
dotctl del MyProfile -y
```

**Options:**

- `--fetch` – Refresh data before removal.
- `-y, --no-confirm` – Skip confirmation prompt.

---

### 🧪 `apply`

Apply a saved profile.

```sh
dotctl apply [-h] [-p <password>] [--skip-sudo] [--skip-hooks] [--skip-pre-hooks] [--skip-post-hooks] [--ignore-hook-errors] [profile]
```

**Examples:**

```sh
dotctl apply
dotctl apply mydesktop --skip-hooks
dotctl apply MyProfile --skip-pre-hooks --ignore-hook-errors
```

**Options:**

- `--skip-sudo` – Ignore restricted resources.
- `--skip-hooks` – Skip all hooks.
- `--skip-pre-hooks` – Skip only pre-hooks.
- `--skip-post-hooks` – Skip only post-hooks.
- `--ignore-hook-errors` – Don’t abort if hooks fail.
- `-p, --password` – Password for restricted actions.

---

### 📤 `export`

Export a profile to `.dtsv`.

```sh
dotctl export [-h] [-p <password>] [--skip-sudo] [profile]
```

**Examples:**

```sh
dotctl export
dotctl export my_web_server --skip-sudo
dotctl export my_web_server -p mYsecretp@ssw0rd
```

**Options:**

- `--skip-sudo`, `-p` same as above.

---

### 📥 `import`

Import a `.dtsv` profile.

```sh
dotctl import [-h] [-p <password>] [--skip-sudo] <file.dtsv>
```

**Examples:**

```sh
dotctl import my_web_server.dtsv
dotctl import /data/backup/web.dtsv --skip-sudo
```

**Options:**

- `--skip-sudo`, `-p` same as above.

---

### 🔥 `wipe`

Remove all local profiles.

```sh
dotctl wipe [-h] [-y]
```

**Examples:**

```sh
dotctl wipe
dotctl wipe -y
```

**Options:**

- `-y, --no-confirm` – Do not prompt before wiping.

---

## 🧑‍💻 Development & Publishing

### Setup Development Environment

```sh
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

### Build the Package

```sh
python -m build
```

### Publish to TestPyPI

```sh
twine upload --repository testpypi dist/*
```

### Publish to PyPI

```sh
twine upload --repository pypi dist/*
```

---

## 🙋 Contact

- **Maintainer:** [Pankaj Jackson](https://github.com/pankajackson)
- **Support:** [Open an Issue](https://github.com/pankajackson/dotctl/issues)
