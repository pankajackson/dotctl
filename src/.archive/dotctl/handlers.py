import os
import subprocess
import shutil
import getpass
from .exception import exception_handler

def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def log(msg, *args, **kwargs):
    print(f"PlasmaSaver: {msg.capitalize()}", *args, **kwargs)


def get_sudo_pass(file, sudo_max_attempts=3):
    s_pass = None
    print("Required sudo to process %s" % str(file))
    print("Please select one option from list:")
    print("     1. Provide sudo Password and apply to recurrence")
    print("     2. Provide sudo Password and apply to current file")
    print("     3. Skip all")
    print("     4. Skip current file")
    sudo_behaviour_status = int(input("Please provide your input [1/2/3/4]: "))
    if sudo_behaviour_status == 1 or sudo_behaviour_status == 2:
        s_pass = getpass.getpass("Please provide password: ")
    if sudo_behaviour_status == 1:
        global sudo_pass
        sudo_pass = s_pass
        return s_pass
    elif sudo_behaviour_status == 2:
        return s_pass
    elif sudo_behaviour_status == 3:
        global skip_sudo
        skip_sudo = True
        return None
    elif sudo_behaviour_status == 4:
        return None
    else:
        log("Error: bad input")
        if sudo_max_attempts > 0:
            log("Error: Input limit exceed")
            return get_sudo_pass(file, sudo_max_attempts=sudo_max_attempts - 1)
        else:
            return None


@exception_handler
def copy(source, dest):
    assert isinstance(source, str) and isinstance(dest, str), "Invalid path"
    assert source != dest, "Source and destination can't be same"
    assert os.path.exists(source), "Source path doesn't exist"

    if not os.path.exists(dest):
        try:
            os.makedirs(dest)
        except PermissionError:
            command = "mkdir -p %s" % dest
            if sudo_pass:
                subprocess.check_output(
                    "echo %s|sudo -S %s; echo $? " % (sudo_pass, command), shell=True
                )
            elif skip_sudo:
                pass
            else:
                temp_pass = get_sudo_pass(dest)
                subprocess.check_output(
                    "echo %s|sudo -S %s; echo $? " % (temp_pass, command), shell=True
                )

    for item in os.listdir(source):
        source_path = os.path.join(source, item)
        dest_path = os.path.join(dest, item)

        if os.path.isdir(source_path):
            copy(source_path, dest_path)
        else:
            if os.path.exists(dest_path):
                try:
                    os.remove(dest_path)
                except PermissionError:
                    command = "rm -rf %s" % dest_path
                    if sudo_pass:
                        subprocess.check_output(
                            "echo %s|sudo -S %s; echo $? " % (sudo_pass, command),
                            shell=True,
                        )
                    elif skip_sudo:
                        pass
                    else:
                        temp_pass = get_sudo_pass(dest_path)
                        subprocess.check_output(
                            "echo %s|sudo -S %s; echo $? " % (temp_pass, command),
                            shell=True,
                        )

            if os.path.exists(source_path):
                try:
                    shutil.copy(source_path, dest)
                except PermissionError:
                    command = "cp %s %s" % (source_path, dest)
                    if sudo_pass:
                        subprocess.check_output(
                            "echo %s|sudo -S %s; echo $? " % (sudo_pass, command),
                            shell=True,
                        )
                    elif skip_sudo:
                        pass
                    else:
                        temp_pass = get_sudo_pass(dest)
                        subprocess.check_output(
                            "echo %s|sudo -S %s; echo $? " % (temp_pass, command),
                            shell=True,
                        )
