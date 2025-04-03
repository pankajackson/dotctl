import subprocess
import getpass
from pathlib import Path
from dotctl.exception import exception_handler
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
        command = ["sshpass", "-p", sudo_pass, "sudo"] + command

    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    stdout, stderr = process.communicate()

    if process.returncode != 0:
        log(f"rsync failed: {stderr.strip()}")

        if "Permission denied" in stderr or process.returncode == 13:
            raise PermissionError(stderr.strip())

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


def run_command(command: str, sudo_pass: str | None = None):
    """Runs a shell command and returns success status, output, and exit code."""
    if sudo_pass:
        command = f"echo {sudo_pass} | sudo -S {command}"

    try:
        result = subprocess.run(
            command, shell=True, check=True, text=True, capture_output=True
        )
        return True, result.stdout.strip(), result.returncode  # Success
    except subprocess.CalledProcessError as e:
        return False, e.stderr.strip() if e.stderr else "", e.returncode  # Failure


@exception_handler
def copy(source: Path, dest: Path, skip_sudo=False, sudo_pass=None):
    """Copies files/directories using rsync and handles sudo permission issues."""
    temp_pass = None
    source_exists = False
    is_dir = False  # Default to file

    try:
        try:
            source_exists = source.exists()
            is_dir = source.is_dir()
        except PermissionError:
            if skip_sudo:
                log(f"PermissionError: skipping {source}")
                return skip_sudo, sudo_pass
            else:
                if not temp_pass and not sudo_pass:
                    temp_pass, sudo_pass, skip_sudo = get_sudo_pass(source)
                success, _, _ = run_command(f"ls {source}", temp_pass or sudo_pass)
                source_exists = success
                _, _, exit_code = run_command(
                    f"test -d {source}", temp_pass or sudo_pass
                )
                is_dir = exit_code == 0

        if source_exists:
            assert source != dest, "Source and destination can't be the same"
            rsync(source, dest, temp_pass or sudo_pass, is_dir=is_dir)
    except PermissionError:
        log(f"PermissionError: {source} requires sudo access.")
        if not skip_sudo:
            temp_pass, sudo_pass, skip_sudo = get_sudo_pass(source)
            if temp_pass or sudo_pass:
                rsync(source, dest, temp_pass or sudo_pass, is_dir=is_dir)

    return skip_sudo, sudo_pass
