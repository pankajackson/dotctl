"""Shared sudo prompting, command execution, and credential helpers."""

import getpass
import subprocess
from pathlib import Path

from dotctl.utils import log

_cached_password: str | None = None
_skip_all = False
_path_passwords: list[tuple[Path, str]] = []


class SudoSkipped(PermissionError):
    """Raised when the user chooses to skip an inaccessible path."""


def run_command(command: list[str], sudo_pass: str | None = None):
    """Run a command, optionally using password or passwordless sudo.

    Returns (success, stdout_or_stderr, return_code).
    """
    stdin = None
    if sudo_pass is not None:
        if sudo_pass:
            command = ["sudo", "-S", "-p", "", *command]
            stdin = f"{sudo_pass}\n"
        else:
            command = ["sudo", "-n", *command]

    try:
        result = subprocess.run(
            command,
            input=stdin,
            check=True,
            text=True,
            capture_output=True,
        )
        return True, result.stdout, result.returncode
    except subprocess.CalledProcessError as error:
        return False, error.stderr if error.stderr else "", error.returncode


def get_sudo_pass(path: Path, sudo_max_attempts: int = 3):
    """Prompt for sudo credentials or a skip choice."""
    log(f"Required sudo to process {path}")
    log("Please select one option from the list:")
    print("     1. Provide sudo Password and apply to recurrence")
    print("     2. Provide sudo Password and apply to current path")
    print("     3. Skip all")
    print("     4. Skip current path")

    try:
        choice = int(input("Please provide your input [1/2/3/4]: "))
    except ValueError:
        log("Invalid input. Please enter a number between 1 and 4.")
        return (
            get_sudo_pass(path, sudo_max_attempts - 1)
            if sudo_max_attempts > 0
            else (None, None, False)
        )

    if choice in (1, 2):
        password = getpass.getpass("Please provide password: ")
        return (None, password, False) if choice == 1 else (password, None, False)
    if choice == 3:
        return None, None, True
    if choice == 4:
        return None, None, False

    log("Error: Invalid input, please enter a number between 1 and 4.")
    return (
        get_sudo_pass(path, sudo_max_attempts - 1)
        if sudo_max_attempts > 0
        else (None, None, False)
    )


def sudo_credential(
    temp_pass: str | None, sudo_pass: str | None
) -> str | None:
    """Prefer a one-operation credential over the recurring credential."""
    return temp_pass if temp_pass is not None else sudo_pass


def request_sudo(path: Path):
    """Try noninteractive access to this path before prompting."""
    probe = path
    while True:
        success, stderr, _ = run_command(["ls", "-ld", str(probe)], "")
        if success:
            return "", None, False
        if "No such file or directory" not in stderr or probe.parent == probe:
            break
        probe = probe.parent
    return get_sudo_pass(path)


def raise_if_sudo_failed(stderr: str) -> None:
    message = stderr.lower()
    if any(
        marker in message
        for marker in (
            "a password is required",
            "interactive authentication is required",
            "sorry, try again",
            "incorrect password",
            "not allowed to execute",
            "permission denied",
        )
    ):
        raise PermissionError(stderr or "Sudo authentication failed")


def run_privileged(
    command: list[str],
    sudo_pass: str | None = None,
    operation: str = "command",
) -> str:
    """Run an operation and translate permission failures consistently."""
    success, output, return_code = run_command(command, sudo_pass)
    if success:
        return output.strip()

    log(f"{operation} failed: {output}")
    raise_if_sudo_failed(output)
    if "Permission denied" in output or return_code == 13:
        raise PermissionError(output)
    raise subprocess.CalledProcessError(return_code, command, output)


def run_for_path(
    command: list[str], path: Path, *, required_sudo: bool = False
) -> str:
    """Run a path operation normally, or through the shared sudo flow."""
    global _cached_password, _skip_all

    if _skip_all:
        raise SudoSkipped(f"Skipped {path}")

    if not required_sudo:
        success, output, return_code = run_command(command)
        if success:
            return output
        try:
            raise_if_sudo_failed(output)
        except PermissionError:
            pass
        else:
            raise subprocess.CalledProcessError(return_code, command, output)

    # First try the actual operation with noninteractive sudo. This respects
    # command-specific sudoers rules (for example, sudo access to cat/find).
    success, output, return_code = run_command(command, "")
    if success:
        return output
    try:
        raise_if_sudo_failed(output)
    except PermissionError:
        pass
    else:
        path_commands = {"ls", "cat", "readlink", "find"}
        command_name = Path(command[0]).name if command else ""
        if command_name not in path_commands or "no such file or directory" in output.lower():
            raise subprocess.CalledProcessError(return_code, command, output)

    credential = _cached_password
    if credential is None:
        credential = next(
            (
                password
                for scope, password in reversed(_path_passwords)
                if path == scope or scope in path.parents
            ),
            None,
        )
    cache_credential = False
    cache_path_credential = False
    if credential is None:
        temp_pass, saved_pass, skip_all = get_sudo_pass(path)
        if skip_all:
            _skip_all = True
            raise SudoSkipped(f"Skipped {path}")
        credential = temp_pass if temp_pass is not None else saved_pass
        if credential is None:
            raise SudoSkipped(f"Skipped {path}")
        cache_credential = saved_pass is not None
        cache_path_credential = temp_pass is not None

    success, output, return_code = run_command(command, credential)
    if success:
        if cache_credential:
            _cached_password = credential
        elif cache_path_credential:
            _path_passwords.append((path, credential))
        return output
    try:
        raise_if_sudo_failed(output)
    except PermissionError:
        raise
    raise subprocess.CalledProcessError(return_code, command, output)


def read_path_text(path: Path, *, required_sudo: bool = False) -> str:
    """Read a text file or symlink target through the shared access flow."""
    if is_symlink(path, required_sudo=required_sudo):
        return run_for_path(
            ["readlink", str(path)], path, required_sudo=required_sudo
        ).rstrip("\n")
    return run_for_path(["cat", str(path)], path, required_sudo=required_sudo)


def list_path_files(
    directory: Path, *, required_sudo: bool = False
) -> list[Path]:
    """List files and symlinks recursively without losing permission errors."""
    command = [
        "find",
        str(directory),
        "(",
        "-type",
        "f",
        "-o",
        "-type",
        "l",
        ")",
        "-print0",
    ]
    try:
        output = run_for_path(command, directory, required_sudo=required_sudo)
    except subprocess.CalledProcessError as error:
        if "No such file or directory" in str(error.stderr):
            return []
        raise
    return [Path(item) for item in output.split("\0") if item]


def path_exists(path: Path, *, required_sudo: bool = False) -> bool:
    try:
        path.lstat()
        return True
    except FileNotFoundError:
        return False
    except PermissionError:
        try:
            run_for_path(
                ["ls", "-ld", str(path)], path, required_sudo=required_sudo
            )
            return True
        except subprocess.CalledProcessError as error:
            if "No such file or directory" in str(error.stderr):
                return False
            raise


def is_directory(path: Path, *, required_sudo: bool = False) -> bool:
    if not path_exists(path, required_sudo=required_sudo):
        return False
    if path.is_dir():
        return True
    try:
        run_for_path(
            ["test", "-d", str(path)], path, required_sudo=required_sudo
        )
        return True
    except subprocess.CalledProcessError:
        return False


def is_symlink(path: Path, *, required_sudo: bool = False) -> bool:
    if path.is_symlink():
        return True
    if not path_exists(path, required_sudo=required_sudo):
        return False
    try:
        run_for_path(
            ["test", "-L", str(path)], path, required_sudo=required_sudo
        )
        return True
    except subprocess.CalledProcessError:
        return False
