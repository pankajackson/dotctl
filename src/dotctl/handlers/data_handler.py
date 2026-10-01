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

    if sudo_pass:
        command = ["sudo", "-S", "-p", ""] + command

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
    if sudo_pass:
        command = ["sudo", "-S", "-p", ""] + command

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
    if sudo_pass:
        command = ["sudo", "-S", "-p", "", *command]
        stdin = f"{sudo_pass}\n"

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
            if not temp_pass and not sudo_pass:
                temp_pass, sudo_pass, skip_sudo = get_sudo_pass(path)
            success, _, _ = run_command(
                ["ls", "-ld", str(path)], temp_pass or sudo_pass
            )
            target_exists = success

    if target_exists:
        try:
            remove_file_or_dir(path, temp_pass or sudo_pass)
        except PermissionError:
            log(f"PermissionError: {path} requires sudo access.")
            if not skip_sudo:
                temp_pass, sudo_pass, skip_sudo = get_sudo_pass(path)
                if temp_pass or sudo_pass:
                    remove_file_or_dir(path, temp_pass or sudo_pass)


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
            if not temp_pass and not sudo_pass:
                temp_pass, sudo_pass, skip_sudo = get_sudo_pass(source)
            success, _, _ = run_command(
                ["ls", "-ld", str(source)], temp_pass or sudo_pass
            )
            source_exists = success
            _, _, exit_code = run_command(
                ["test", "-d", str(source)], temp_pass or sudo_pass
            )
            is_dir = exit_code == 0
    if source_exists:
        try:
            assert source != dest, "Source and destination can't be the same"
            rsync(source, dest, temp_pass or sudo_pass, is_dir=is_dir)
        except PermissionError:
            log(f"PermissionError: {source} requires sudo access.")
            if not skip_sudo:
                temp_pass, sudo_pass, skip_sudo = get_sudo_pass(source)
                if temp_pass or sudo_pass:
                    rsync(source, dest, temp_pass or sudo_pass, is_dir=is_dir)
    else:
        if prune:
            log(f'Removing "{dest.parent.name}:{dest.name}"...')
            delete(dest, skip_sudo, temp_pass or sudo_pass)

    return skip_sudo, sudo_pass
