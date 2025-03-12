# DotCtl

A CLI Tool to Manage DOT Files/Settings/Configurations.

## Features

- Save Profile: Save existing dot files/config/settings.
- Import Profile: Import existing dot files/config/settings from a `.plsv` file.
- Export Profile: Export and share existing dot files/config/settings to a `.plsv` file.
- Manage multiple profiles with ease.

## Installation

```sh
pip install dotctl
```

## CLI Guide

### Save Profile

```sh
dotctl save <profile_name>
```

**Example:**

```sh
dotctl save MyProfile
```

**Options:**

- `-f, --force` → Overwrite already saved profiles.
- `-c <path>, --config-file <path>` → Use external config file.
- `-e <env>, --env <env>` → Desktop environment (e.g., KDE).
- `-p <password>, --password <password>` → Sudo Password to authorize restricted data (e.g., `/usr/share`).
- `--include-global` → Include data from the global data directory (`/usr/share`).
- `--include-sddm` → Include SDDM data/configs (`/usr/share/sddm`, `/etc/sddm.conf.d`).
- `--sddm-only` → Operate only on SDDM configurations (**Note:** Requires sudo password).
- `--skip-sudo` → Skip all sudo operations.

### Remove Profile

```sh
dotctl remove <profile_name>
```

**Example:**

```sh
dotctl remove MyProfile
```

### List Profiles

```sh
dotctl list
```

### Apply Profile

```sh
dotctl apply <profile_name>
```

**Example:**

```sh
dotctl apply MyProfile
```

**Options:**

- `-p <password>, --password <password>` → Sudo Password for restricted data.
- `--sddm-only` → Apply only SDDM configurations (**Requires sudo password**).
- `--skip-global` → Skip data from the global directory (`/usr/share`).
- `--skip-sddm` → Skip SDDM configurations.
- `--skip-sudo` → Skip all sudo operations.

### Import Profile

```sh
dotctl import <profile_path>
```

**Example:**

```sh
dotctl import MyProfile.plsv
```

**Options:**

- `-p <password>, --password <password>` → Sudo Password for restricted data.
- `--config-only` → Apply only dot files/configurations (`~/.config`).
- `--data-only` → Apply only dot files/data (`~/.local/share`).
- `--sddm-only` → Apply only SDDM configurations (**Requires sudo password**).
- `--skip-global` → Skip global data.
- `--skip-sddm` → Skip SDDM configurations.
- `--skip-sudo` → Skip all sudo operations.

### Export Profile

```sh
dotctl export <profile_path>
```

**Example:**

```sh
dotctl export MyProfile.plsv
```

**Options:**

- `-p <password>, --password <password>` → Sudo Password for restricted data.
- `--config-only` → Export only dot files/configurations.
- `--data-only` → Export only dot files/data.
- `--sddm-only` → Export only SDDM configurations (**Requires sudo password**).
- `--skip-global` → Skip global data.
- `--skip-sddm` → Skip SDDM configurations.
- `--skip-sudo` → Skip all sudo operations.

### Wipe All Profiles

```sh
dotctl wipe
```

### Help

```sh
dotctl -h
dotctl <action> -h
```

**Example:**

```sh
dotctl import -h
```

### Version

```sh
dotctl -v
```

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
