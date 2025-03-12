import subprocess
import shutil
import getpass
from pathlib import Path
from dotctl.exception import exception_handler
from dotctl.utils import log


def get_sudo_pass(file, sudo_max_attempts=3):
    """Prompt for sudo password and handle user choices."""
    global sudo_pass, skip_sudo

    print(f"Required sudo to process {file}")
    print("Please select one option from the list:")
    print("     1. Provide sudo Password and apply to recurrence")
    print("     2. Provide sudo Password and apply to current file")
    print("     3. Skip all")
    print("     4. Skip current file")

    try:
        sudo_behaviour_status = int(input("Please provide your input [1/2/3/4]: "))
    except ValueError:
        log("Invalid input. Please enter a number between 1 and 4.")
        return (
            get_sudo_pass(file, sudo_max_attempts - 1)
            if sudo_max_attempts > 0
            else None
        )

    if sudo_behaviour_status in {1, 2}:
        s_pass = getpass.getpass("Please provide password: ")
        if sudo_behaviour_status == 1:
            sudo_pass = s_pass
        return s_pass
    elif sudo_behaviour_status == 3:
        skip_sudo = True
        return None
    elif sudo_behaviour_status == 4:
        return None
    else:
        log("Error: Invalid input")
        return (
            get_sudo_pass(file, sudo_max_attempts - 1)
            if sudo_max_attempts > 0
            else None
        )


def run_sudo_command(command, sudo_pass):
    """Run a shell command with sudo, using the provided password."""
    if sudo_pass:
        try:
            subprocess.check_output(
                f"echo {sudo_pass} | sudo -S {command}",
                shell=True,
                stderr=subprocess.DEVNULL,
            )
        except subprocess.CalledProcessError:
            log(f"Failed to execute: {command}")
    else:
        log(f"Skipping sudo command: {command}")


@exception_handler
def copy(source: Path, dest: Path, skip_sudo=False, sudo_pass=None):
    """Copy files and directories with sudo handling."""

    # No source to copy, just clean up destination if necessary
    if not source.exists():
        if dest.exists():
            try:
                if dest.is_dir():
                    shutil.rmtree(dest)
                else:
                    dest.unlink()
            except PermissionError:
                if not skip_sudo:
                    temp_pass = sudo_pass or get_sudo_pass(dest)
                    if temp_pass:
                        run_sudo_command(f"rm -rf {dest}", temp_pass)
        return

    assert source != dest, "Source and destination can't be the same"

    # If the source is a file, just copy it over, overwriting if necessary
    if source.is_file():
        if dest.exists():
            try:
                dest.unlink()
            except PermissionError:
                if not skip_sudo:
                    temp_pass = sudo_pass or get_sudo_pass(dest)
                    if temp_pass:
                        run_sudo_command(f"rm -f {dest}", temp_pass)

        try:
            shutil.copy2(source, dest)
        except PermissionError:
            if not skip_sudo:
                temp_pass = sudo_pass or get_sudo_pass(dest)
                if temp_pass:
                    run_sudo_command(f"cp {source} {dest}", temp_pass)
        return

    # If source is a directory, create the destination if needed
    if not dest.exists():
        try:
            dest.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            if not skip_sudo:
                temp_pass = sudo_pass or get_sudo_pass(dest)
                if temp_pass:
                    run_sudo_command(f"mkdir -p {dest}", temp_pass)

    # Recursively copy contents
    for item in source.iterdir():
        source_path = source / item.name
        dest_path = dest / item.name
        copy(source_path, dest_path, skip_sudo=skip_sudo, sudo_pass=sudo_pass)
