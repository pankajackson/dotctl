# DotCtl

**dotctl** is a powerful CLI tool to profile your OS by saving, applying, exporting, and importing system configurations
as named profiles. Designed to manage dotfiles and service configurations in a centralized Git repository
(local or remote), dotctl enables seamless system replication across machines. Supports pre/post hook scripts,
making it ideal for setting up servers or desktops with consistent environments

## Table of Contents

- [DotCtl](#dotctl)
  - [Table of Contents](#table-of-contents)
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
  - [Development \& Publishing Guide](#development--publishing-guide)
    - [Setup Development Environment](#setup-development-environment)
    - [Build the Package](#build-the-package)
    - [Publish to TestPyPI](#publish-to-testpypi)
    - [Publish to PyPI](#publish-to-pypi)
  - [Who do I talk to?](#who-do-i-talk-to)

---

## 🚀 Features

- 📦 **Profile Management** — Create, list, switch, remove, save, and apply system profiles.
- 🌀 **Pre/Post Hooks** — Run self managed scripts before or after applying a profile (e.g. install packages, restart services).
- 🔄 **Git Integration** — Sync profiles with local or remote Git repositories.
- 📁 **Data Sync** — Export/import full configurations with `.dtsv` files for easy sharing and backup.
- 🧩 **Custom Configuration** — Use a `dotctl.yaml` to define how and what gets tracked in a profile.

## 🔧 Installation

```sh
pip install dotctl
```

## 📘 Usage

```bash
dotctl [OPTIONS] <COMMAND> [ARGS]
```

Run `dotctl -h` for help.

## 🛠️ Commands

### 📁 `init`

Initialize a new profile and optionally link it to a Git repo.

- **Syntax**

  ```bash
  usage: dotctl init [-h] [-u <git-url>] [-p <profile>] [-c <path>] [-e <env>]
  ```

- **Example**

  ```bash
  # initialize a profile for kde environment
  dotctl init -e kde

  # initialize a profile for a remote repo and activate profile mydesktop
  dotctl init -u https://github.com/user880/dots.git -p mydesktop

  # initialize a profile with a custom config
  dotctl init -c ./my_custom_config.yaml
  ```

- **Options**

  - `-e, --env` : Environment to initialize the profile for.
  - `-u, --url` : git URL to fetch the profile from.
  - `-p, --profile` : Profile to initialize after initialization.
  - `-c, --config` : Path to a custom config file.

### 💾 `save`

Save the current system state and configuration to the active profile.

- **Syntax**

  ```bash
  usage: dotctl save [-h] [-p <password>] [--skip-sudo] [profile]
  ```

- **Example**

  ```bash
  dotctl save
  dotctl save my_web_server
  dotctl save my_web_server --skip-sudo
  dotctl save my_web_server -p mYsecretp@ssw0rd
  ```

- **Options**

  - `--skip-sudo` - Skip the sudo prompt to ignore restricted resources.
  - `-p, --password` - Password to access restricted resources.

### 📋 `list` / `ls`

List all profiles, optionally show details or fetch remote info.

- **Syntax**

  ```bash
  usage: dotctl list [-h] [--details] [--fetch]
  ```

- **Example**

  ```bash
  dotctl list
  dotctl list --details
  dotctl list --fetch
  ```

- **Options**

  - `--details` - Show details of the profile.
  - `--fetch` - Fetch/update remote info before listing.

### 🔀 `switch` / `sw`

Switch to another profile.

- **Syntax**

  ```bash
  usage: dotctl switch [-h] [--fetch] [profile]
  ```

- **Example**

  ```bash
  dotctl sw MyProfile
  dotctl switch MyProfile --fetch
  ```

- **Options**

  - `--fetch` - Fetch/update remote info before switching.

### 🆕 `create` / `new`

Create a new empty profile.

- **Syntax**

  ```bash
  usage: dotctl create [-h] [--fetch] profile
  ```

- **Example**

  ```bash
  dotctl create MyProfile
  dotctl new MyProfile --fetch
  ```

- **Options**

  - `--fetch` - Fetch/update remote info before listing.

### ❌ `remove` / `rm` / `delete` / `del`

Delete an existing profile locally and/or remotely.

- **Syntax**

  ```bash
  usage: dotctl remove [-h] [-y] [--fetch] profile
  ```

- **Example**

  ```bash
  dotctl rm MyProfile
  dotctl del MyProfile --fetch
  dotctl del MyProfile --no-confirm
  ```

- **Options**

  - `--fetch` - Fetch/update remote info before listing.
  - `-y, --no-confirm` - Do not prompt for confirmation before deleting.

### 🧪 `apply`

Apply a saved profile to your current machine.

- **Syntax**

  ```bash
  usage: dotctl apply [-h] [-p <password>] [--skip-sudo] [--skip-hooks] [--skip-pre-hooks] [--skip-post-hooks] [--ignore-hook-errors] [profile]
  ```

- **Example**

  ```bash
  dotctl apply
  dotctl apply MyProfile
  dotctl apply MyProfile --skip-sudo
  dotctl apply MyProfile --password mYsecretp@ssw0rd
  dotctl apply MyProfile --skip-hooks
  dotctl apply MyProfile --skip-pre-hooks
  dotctl apply MyProfile --skip-post-hooks
  dotctl apply --ignore-hook-errors
  ```

- **Options**

  - `-p, --password` - Password to access restricted resources.
  - `--skip-sudo` - Skip the sudo prompt to ignore restricted resources.
  - `--skip-hooks`: Skip the hooks.
  - `--skip-pre-hooks`: Skip the pre-hooks.
  - `--skip-post-hooks`: Skip the post-hooks.
  - `--ignore-hook-errors`: Ignore errors in hooks.

- **Fine-grained control**

  - `--skip-pre-hooks`
  - `--skip-post-hooks`
  - `--ignore-hook-errors`

### 📤 `export`

Export a profile (along with data) into a `.dtsv` file.

- **Syntax**

  ```bash
  usage: dotctl export [-h] [-p <password>] [--skip-sudo] [profile]
  ```

- **Example**

  ```bash
  dotctl export
  dotctl export my_web_server
  dotctl export my_web_server --skip-sudo
  dotctl export my_web_server -p mYsecretp@ssw0rd
  ```

- **Options**

  - `--skip-sudo` - Skip the sudo prompt to ignore restricted resources.
  - `-p, --password` - Password to access restricted resources.

### 📥 `import`

Import a `.dtsv` profile from another system.

- **Syntax**

  ```bash
  usage: dotctl import [-h] [-p <password>] [--skip-sudo] profile_file.dtsv
  ```

- **Example**

  ```bash
  dotctl import my_web_server.dtsv
  dotctl import /data/backup/my_web_server.dtsv --skip-sudo
  dotctl import my_web_server.dtsv -p mYsecretp@ssw0rd
  ```

- **Options**

  - `--skip-sudo` - Skip the sudo prompt to ignore restricted resources.
  - `-p, --password` - Password to access restricted resources.

### 🔥 `wipe`

Wipe all profiles from the local system.

- **Syntax**

  ```bash
  usage: dotctl wipe [-h] [-y]
  ```

- **Example**

  ```bash
  dotctl wipe
  dotctl wipe -y
  ```

- **Options**

  - `-y, --no-confirm`: Do not prompt for confirmation before wiping profiles.

---

## Development & Publishing Guide

### Setup Development Environment

```sh
# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Linux/macOS
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

### Build the Package

```sh
python -m build
```

This will generate a `dist/` directory with `.tar.gz` and `.whl` files.

### Publish to TestPyPI

```sh
twine upload --repository testpypi dist/*
```

### Publish to PyPI

```sh
twine upload --repository pypi dist/*
```

---

## Who do I talk to?

- **Repo Owner/Admin:** Pankaj Jackson
- **Community Support:** Reach out via GitHub Issues
