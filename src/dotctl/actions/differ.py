from dataclasses import dataclass
from pathlib import Path
import sys

from dotctl.paths import app_profile_directory, app_config_file
from dotctl.handlers.config_handler import conf_reader
from dotctl.handlers.diff_handler import (
    get_file_diff,
    render_side_by_side,
    render_colored_diff,
    is_target_match,
)
from dotctl.handlers.git_handler import get_repo
from dotctl.utils import log


@dataclass
class DiffProps:
    profile_dir: Path
    target: str | None
    color: bool
    side_by_side: bool


differ_default_props = DiffProps(
    profile_dir=Path(app_profile_directory),
    target=None,
    color=False,
    side_by_side=False,
)


def diff(props: DiffProps) -> None:
    repo = get_repo(props.profile_dir)

    if repo.bare:
        log("❌ The repository is bare. No Profile available.")
        sys.exit(1)

    config = conf_reader(config_file=Path(app_config_file))

    changes_found = False

    target_path = Path(props.target).expanduser().resolve() if props.target else None

    for name, section in config.save.items():

        source_base_dir = Path(section.location)
        repo_base_dir = props.profile_dir / name

        for entry in section.entries:

            source = source_base_dir / entry
            repo_file = repo_base_dir / entry
            if target_path is not None:
                if not is_target_match(
                    target=target_path,
                    source=source,
                    repo_file=repo_file,
                ):
                    continue
            diff_lines = get_file_diff(source, repo_file)

            if diff_lines:
                changes_found = True

                log(f"\n🔍 Diff: {name}/{entry}")
                if props.side_by_side:
                    render_side_by_side(source, repo_file)

                elif props.color:
                    render_colored_diff(diff_lines)

                else:
                    print("".join(diff_lines))

    if not changes_found:
        log("✅ No differences detected.")
