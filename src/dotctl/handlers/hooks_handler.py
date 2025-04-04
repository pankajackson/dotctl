from pathlib import Path
from dotctl.paths import app_hooks_directory
from dotctl import __BASE_DIR__
from dotctl.utils import log
from .data_handler import copy


def hooks_initializer(app_hooks_dir_path: Path = Path(app_hooks_directory)):
    app_hooks_dir_path.mkdir(parents=True, exist_ok=True)
    hooks_base_dir = Path(__BASE_DIR__) / "hooks"
    copy(hooks_base_dir, app_hooks_dir_path)
