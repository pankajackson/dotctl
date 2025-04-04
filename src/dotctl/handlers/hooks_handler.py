import subprocess
import threading
from pathlib import Path
from dotctl import __BASE_DIR__
from dotctl.paths import app_hooks_directory
from dotctl.utils import log
from .data_handler import copy


def hooks_initializer(app_hooks_dir_path: Path = Path(app_hooks_directory)):
    app_hooks_dir_path.mkdir(parents=True, exist_ok=True)
    hooks_base_dir = Path(__BASE_DIR__) / "hooks"
    copy(hooks_base_dir, app_hooks_dir_path)


def run_shell_script(
    script_path: Path,
    args: list[str] = [],
    on_output=None,
    input_lines=None,
    timeout: int = 30,
    ignore_errors: bool = False,
):
    """
    Runs a shell script with real-time output and optional stdin input.

    :param script_path: Path to the .sh script
    :param args: List of arguments to pass to the script
    :param on_output: Optional function to process each line of output
    :param input_lines: Optional list of lines to send to stdin
    :param timeout: Optional timeout in seconds
    :param ignore_errors: If True, script failures (non-zero exit code) are ignored
    :return: Exit code of the process
    """
    if args is None:
        args = []

    cmd = ["bash", str(script_path)] + args

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        stdin=subprocess.PIPE,
        text=True,
        bufsize=1,
    )

    def stream_output():
        if process.stdout:
            for line in process.stdout:
                if on_output:
                    on_output(line)
                else:
                    print(line, end="")

    output_thread = threading.Thread(target=stream_output)
    output_thread.start()

    if input_lines and process.stdin:
        for line in input_lines:
            process.stdin.write(line + "\n")
        process.stdin.flush()

    try:
        process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        process.kill()
        msg = f"❌ Script '{script_path}' timed out and was terminated."
        if not ignore_errors:
            raise RuntimeError(msg)
        if on_output:
            on_output(msg)
        else:
            print(msg)
        return -1

    output_thread.join()

    if process.returncode != 0:
        msg = f"❌ Script '{script_path}' exited with code {process.returncode}"
        if not ignore_errors:
            raise RuntimeError(msg)
        if on_output:
            on_output(msg)
        else:
            print(msg)

    return process.returncode


def run_hooks(
    app_hooks_dir_path: Path = Path(app_hooks_directory),
    pre_apply_hooks: bool = False,
    post_apply_hooks: bool = False,
    ignore_errors: bool = False,
):
    if pre_apply_hooks:
        log("Applying pre-apply hooks...")
        script_file = app_hooks_dir_path / "pre_apply.sh"
        run_shell_script(
            script_file, timeout=60, on_output=log, ignore_errors=ignore_errors
        )

    if post_apply_hooks:
        log("Applying post-apply hooks...")
        script_file = app_hooks_dir_path / "post_apply.sh"
        run_shell_script(
            script_file, timeout=60, on_output=log, ignore_errors=ignore_errors
        )
