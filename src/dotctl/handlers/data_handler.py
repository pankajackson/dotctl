import subprocess
from pathlib import Path
from dotctl.utils import log
from dotctl.handlers.sudo_handler import (
    raise_if_sudo_failed,
    request_sudo,
    run_command,
    run_privileged,
    sudo_credential,
)


def rsync(
    source: Path, destination: Path, sudo_pass: str | None = None, is_dir: bool = False
):
    """Synchronizes source to destination using rsync with optional sudo support."""
    rsync_command = "rsync"
    exclude_patterns = ["*.pyc", "*.pyo", ".git"]
    exclude_options = [f"--exclude={pattern}" for pattern in exclude_patterns]
    rsync_options = ["-az", "--delete"]

    source_str = str(source) + "/" if is_dir else str(source)
    destination_str = str(destination) + "/" if is_dir else str(destination)

    command = [
        rsync_command,
        *rsync_options,
        *exclude_options,
        source_str,
        destination_str,
    ]

    return run_privileged(command, sudo_pass, operation="rsync")


def remove_file_or_dir(
    location: Path,
    sudo_pass: str | None = None,
):
    command = ["rm", "-rf", str(location)]
    return run_privileged(command, sudo_pass, operation="cleanup")


def path_exists(path: Path) -> bool:
    """
    Reliable existence check that raises PermissionError
    instead of silently returning False.
    """
    try:
        path.stat()
        return True
    except FileNotFoundError:
        return False


def delete(path: Path, skip_sudo=False, sudo_pass: str | None = None):
    temp_pass = None
    target_exists = False
    try:
        target_exists = path_exists(path)
    except PermissionError:
        if skip_sudo:
            log(f"PermissionError: skipping {path}")
            return skip_sudo, sudo_pass
        else:
            if sudo_credential(temp_pass, sudo_pass) is None:
                temp_pass, sudo_pass, skip_sudo = request_sudo(path)
            if skip_sudo:
                return skip_sudo, sudo_pass
            credential = sudo_credential(temp_pass, sudo_pass)
            if credential is None:
                return skip_sudo, sudo_pass
            success, stderr, _ = run_command(
                ["ls", "-ld", str(path)], credential
            )
            if not success:
                raise_if_sudo_failed(stderr)
            target_exists = success

    if target_exists:
        try:
            remove_file_or_dir(path, sudo_credential(temp_pass, sudo_pass))
        except PermissionError:
            log(f"PermissionError: {path} requires sudo access.")
            if not skip_sudo:
                temp_pass, sudo_pass, skip_sudo = request_sudo(path)
                if temp_pass is not None or sudo_pass is not None:
                    remove_file_or_dir(path, sudo_credential(temp_pass, sudo_pass))


def copy(
    source: Path,
    dest: Path,
    skip_sudo=False,
    sudo_pass=None,
    prune=False,
    sudo: bool = False,
):
    """Copies files/directories using rsync and handles sudo permission issues."""
    temp_pass = None
    source_exists = False
    is_dir = False  # Default to file

    if sudo and sudo_credential(temp_pass, sudo_pass) is None:
        # Empty credential selects `sudo -n` in the shared command runner.
        temp_pass = ""

    try:
        source_exists = path_exists(source)
        is_dir = source.is_dir()
    except PermissionError:
        if skip_sudo:
            log(f"PermissionError: skipping {source}")
            return skip_sudo, sudo_pass
        else:
            if sudo_credential(temp_pass, sudo_pass) is None:
                temp_pass, sudo_pass, skip_sudo = request_sudo(source)
            if skip_sudo:
                return skip_sudo, sudo_pass
            credential = sudo_credential(temp_pass, sudo_pass)
            if credential is None:
                return skip_sudo, sudo_pass
            success, stderr, _ = run_command(
                ["ls", "-ld", str(source)], credential
            )
            if not success and credential == "":
                temp_pass, sudo_pass, skip_sudo = request_sudo(source)
                if skip_sudo:
                    return skip_sudo, sudo_pass
                credential = sudo_credential(temp_pass, sudo_pass)
                if credential is None:
                    return skip_sudo, sudo_pass
                success, stderr, _ = run_command(
                    ["ls", "-ld", str(source)], credential
                )
            if not success:
                raise_if_sudo_failed(stderr)
            source_exists = success
            _, _, exit_code = run_command(
                ["test", "-d", str(source)], credential
            )
            is_dir = exit_code == 0
    if source_exists:
        try:
            assert source != dest, "Source and destination can't be the same"

            try:
                dest.parent.mkdir(parents=True, exist_ok=True)
            except PermissionError:
                if skip_sudo:
                    log(f"PermissionError: skipping destination {dest.parent}")
                    return skip_sudo, sudo_pass

                if sudo_credential(temp_pass, sudo_pass) is None:
                    temp_pass, sudo_pass, skip_sudo = request_sudo(dest.parent)

                parent_pass = sudo_credential(temp_pass, sudo_pass)
                if parent_pass is None:
                    return skip_sudo, sudo_pass

                success, stderr, exit_code = run_command(
                    ["mkdir", "-p", str(dest.parent)], parent_pass
                )
                if not success and parent_pass == "":
                    temp_pass, sudo_pass, skip_sudo = request_sudo(dest.parent)
                    if skip_sudo:
                        return skip_sudo, sudo_pass
                    parent_pass = sudo_credential(temp_pass, sudo_pass)
                    if parent_pass is None:
                        return skip_sudo, sudo_pass
                    success, stderr, exit_code = run_command(
                        ["mkdir", "-p", str(dest.parent)], parent_pass
                    )
                if not success:
                    raise_if_sudo_failed(stderr)
                    raise subprocess.CalledProcessError(
                        exit_code,
                        ["sudo", "-S", "-p", "", "mkdir", "-p", str(dest.parent)],
                        stderr,
                    )

            rsync(source, dest, sudo_credential(temp_pass, sudo_pass), is_dir=is_dir)
        except PermissionError:
            log(f"PermissionError: {source} requires sudo access.")
            if not skip_sudo:
                temp_pass, sudo_pass, skip_sudo = request_sudo(source)
                credential = sudo_credential(temp_pass, sudo_pass)
                if credential is not None:
                    rsync(source, dest, credential, is_dir=is_dir)
    else:
        if prune:
            log(f'Removing "{dest.parent.name}:{dest.name}"...')
            delete(dest, skip_sudo, sudo_credential(temp_pass, sudo_pass))

    return skip_sudo, sudo_pass
