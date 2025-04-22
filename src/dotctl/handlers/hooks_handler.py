import subprocess
import threading
from pathlib import Path
from dotctl import __BASE_DIR__
from dotctl.paths import app_hooks_directory
from dotctl.utils import log, new_line
from .data_handler import copy


def hooks_initializer(
    app_hooks_dir_path: Path = Path(app_hooks_directory),
) -> list[Path]:
    app_hooks_dir_path.mkdir(parents=True, exist_ok=True)
    hooks_base_dir = Path(__BASE_DIR__) / "hooks"

    initialized_hooks = []
    for hook_file in hooks_base_dir.iterdir():
        target_file = app_hooks_dir_path / hook_file.name
        if not target_file.exists():
            copy(hook_file, target_file)
            initialized_hooks.append(hook_file.name)

    return initialized_hooks


def run_shell_script(
    script_path: Path,
    args: list[str] = [],
    timeout: int = 0,
    ignore_errors: bool = False,
):
    """
    Runs a shell script with full interactive terminal support.

    :param script_path: Path to the .sh script
    :param args: List of arguments to pass to the script
    :param timeout: Timeout in seconds (0 = no timeout)
    :param ignore_errors: If True, script failures (non-zero exit code) are ignored
    :return: Exit code of the process
    """
    if args is None:
        args = []

    cmd = ["bash", str(script_path)] + args

    try:
        result = subprocess.run(
            cmd, check=not ignore_errors, timeout=timeout if timeout > 0 else None
        )

        if result.returncode != 0:
            new_line()
            msg = f"❌ Script '{script_path}' exited with code {result.returncode}"
            if not ignore_errors:
                raise RuntimeError(msg)
            log(msg)
        return result.returncode
    except subprocess.TimeoutExpired:
        new_line()
        msg = f"❌ Script '{script_path}' timed out and was terminated."
        if not ignore_errors:
            raise RuntimeError(msg)
        log(msg)
        return -1
    except subprocess.CalledProcessError as e:
        new_line()
        msg = f"❌ Script '{script_path}' exited with code {e.returncode}"
        if not ignore_errors:
            raise RuntimeError(msg)
        log(msg)
        return e.returncode


def run_hooks(
    app_hooks_dir_path: Path = Path(app_hooks_directory),
    pre_apply_hooks: bool = False,
    post_apply_hooks: bool = False,
    ignore_errors: bool = False,
    timeout: int = 0,
):
    if pre_apply_hooks:
        log("Applying pre-apply hooks...")
        script_file = app_hooks_dir_path / "pre_apply.sh"
        run_shell_script(script_file, timeout=timeout, ignore_errors=ignore_errors)

    if post_apply_hooks:
        log("Applying post-apply hooks...")
        script_file = app_hooks_dir_path / "post_apply.sh"
        run_shell_script(script_file, timeout=timeout, ignore_errors=ignore_errors)
