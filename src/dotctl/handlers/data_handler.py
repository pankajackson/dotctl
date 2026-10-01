import subprocess
import getpass
from pathlib import Path
from dotctl.utils import log


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

    if sudo_pass is not None:
        command = (
            ["sudo", "-S", "-p", "", *command]
            if sudo_pass
            else ["sudo", "-n", *command]
        )

    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    stdout, stderr = process.communicate(
        input=f"{sudo_pass}\n" if sudo_pass else None
    )

    if process.returncode != 0:
        log(f"rsync failed: {stderr.strip()}")

        if "Permission denied" in stderr or process.returncode == 13:
            raise PermissionError(stderr.strip())

        raise subprocess.CalledProcessError(process.returncode, command, stderr)

    return stdout.strip()


def remove_file_or_dir(
    location: Path,
    sudo_pass: str | None = None,
):
    command = ["rm", "-rf", str(location)]
    if sudo_pass is not None:
        command = (
            ["sudo", "-S", "-p", "", *command]
            if sudo_pass
            else ["sudo", "-n", *command]
        )

    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    stdout, stderr = process.communicate(
        input=f"{sudo_pass}\n" if sudo_pass else None
    )

    if process.returncode != 0:
        log(f"cleanup failed: {stderr.strip()}")

        if "Permission denied" in stderr or process.returncode == 13:
            raise PermissionError(stdout.strip() or stderr.strip())

        raise subprocess.CalledProcessError(process.returncode, command, stderr)

    return stdout.strip()


def get_sudo_pass(path: Path, sudo_max_attempts: int = 3):
    """Prompt for sudo password and handle user choices."""
    log(f"Required sudo to process {path}")
    log("Please select one option from the list:")
    print("     1. Provide sudo Password and apply to recurrence")
    print("     2. Provide sudo Password and apply to current path")
    print("     3. Skip all")
    print("     4. Skip current path")

    try:
        sudo_behaviour_status = int(input("Please provide your input [1/2/3/4]: "))
    except ValueError:
        log("Invalid input. Please enter a number between 1 and 4.")
        return (
            get_sudo_pass(path, sudo_max_attempts - 1)
            if sudo_max_attempts > 0
            else (None, None, False)
        )

    if sudo_behaviour_status in (1, 2):
        s_pass = getpass.getpass("Please provide password: ")
        return (
            (None, s_pass, False)
            if sudo_behaviour_status == 1
            else (s_pass, None, False)
        )

    if sudo_behaviour_status == 3:
        return None, None, True  # Skip all

    if sudo_behaviour_status == 4:
        return None, None, False  # Skip only current file

    log("Error: Invalid input, please enter a number between 1 and 4.")
    return (
        get_sudo_pass(path, sudo_max_attempts - 1)
        if sudo_max_attempts > 0
        else (None, None, False)
    )


def run_command(command: list[str], sudo_pass: str | None = None):
    """Runs a command without a shell and returns its output and exit code."""
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
        return True, result.stdout.strip(), result.returncode  # Success
    except subprocess.CalledProcessError as e:
        return False, e.stderr.strip() if e.stderr else "", e.returncode  # Failure


def _sudo_credential(temp_pass: str | None, sudo_pass: str | None) -> str | None:
    return temp_pass if temp_pass is not None else sudo_pass


def _request_sudo(path: Path):
    """Use passwordless sudo when available, prompting only if needed."""
    # Probe access to the protected path itself. Some sudoers policies grant
    # passwordless access to file operations without granting `sudo true`.
    success, _, _ = run_command(["ls", "-ld", str(path)], "")
    if success:
        return "", None, False
    return get_sudo_pass(path)


def _raise_if_sudo_failed(stderr: str) -> None:
    message = stderr.lower()
    if any(
        marker in message
        for marker in (
            "a password is required",
            "sorry, try again",
            "incorrect password",
            "not allowed to execute",
            "permission denied",
        )
    ):
        raise PermissionError(stderr or "Sudo authentication failed")


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
            if _sudo_credential(temp_pass, sudo_pass) is None:
                temp_pass, sudo_pass, skip_sudo = _request_sudo(path)
            if skip_sudo:
                return skip_sudo, sudo_pass
            credential = _sudo_credential(temp_pass, sudo_pass)
            if credential is None:
                return skip_sudo, sudo_pass
            success, stderr, _ = run_command(
                ["ls", "-ld", str(path)], credential
            )
            if not success:
                _raise_if_sudo_failed(stderr)
            target_exists = success

    if target_exists:
        try:
            remove_file_or_dir(path, _sudo_credential(temp_pass, sudo_pass))
        except PermissionError:
            log(f"PermissionError: {path} requires sudo access.")
            if not skip_sudo:
                temp_pass, sudo_pass, skip_sudo = _request_sudo(path)
                if temp_pass is not None or sudo_pass is not None:
                    remove_file_or_dir(path, _sudo_credential(temp_pass, sudo_pass))


def copy(source: Path, dest: Path, skip_sudo=False, sudo_pass=None, prune=False):
    """Copies files/directories using rsync and handles sudo permission issues."""
    temp_pass = None
    source_exists = False
    is_dir = False  # Default to file

    try:
        source_exists = path_exists(source)
        is_dir = source.is_dir()
    except PermissionError:
        if skip_sudo:
            log(f"PermissionError: skipping {source}")
            return skip_sudo, sudo_pass
        else:
            if _sudo_credential(temp_pass, sudo_pass) is None:
                temp_pass, sudo_pass, skip_sudo = _request_sudo(source)
            if skip_sudo:
                return skip_sudo, sudo_pass
            credential = _sudo_credential(temp_pass, sudo_pass)
            if credential is None:
                return skip_sudo, sudo_pass
            success, stderr, _ = run_command(
                ["ls", "-ld", str(source)], credential
            )
            if not success:
                _raise_if_sudo_failed(stderr)
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

                if _sudo_credential(temp_pass, sudo_pass) is None:
                    temp_pass, sudo_pass, skip_sudo = _request_sudo(dest.parent)

                parent_pass = _sudo_credential(temp_pass, sudo_pass)
                if parent_pass is None:
                    return skip_sudo, sudo_pass

                success, stderr, exit_code = run_command(
                    ["mkdir", "-p", str(dest.parent)], parent_pass
                )
                if not success:
                    raise subprocess.CalledProcessError(
                        exit_code,
                        ["sudo", "-S", "-p", "", "mkdir", "-p", str(dest.parent)],
                        stderr,
                    )

            rsync(source, dest, _sudo_credential(temp_pass, sudo_pass), is_dir=is_dir)
        except PermissionError:
            log(f"PermissionError: {source} requires sudo access.")
            if not skip_sudo:
                temp_pass, sudo_pass, skip_sudo = _request_sudo(source)
                credential = _sudo_credential(temp_pass, sudo_pass)
                if credential is not None:
                    rsync(source, dest, credential, is_dir=is_dir)
    else:
        if prune:
            log(f'Removing "{dest.parent.name}:{dest.name}"...')
            delete(dest, skip_sudo, _sudo_credential(temp_pass, sudo_pass))

    return skip_sudo, sudo_pass
