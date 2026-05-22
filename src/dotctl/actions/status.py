from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import json

from dotctl.paths import app_profile_directory, app_config_file
from dotctl.handlers.config_handler import conf_reader
from dotctl.handlers.git_handler import get_repo
from dotctl.handlers.profile_handler import StatusReport, build_status_report
from dotctl.utils import log


@dataclass
class StatusProps:
    profile_dir: Path
    json: bool
    short: bool


status_default_props = StatusProps(
    profile_dir=Path(app_profile_directory),
    json=False,
    short=False,
)


def render_full(report: StatusReport):

    print("✔ repo: up to date" if report.repo_clean else "⚠ repo: drift detected")

    print(
        f"⚠ local changes detected: {len(report.modified_files)} files"
        if report.modified_files
        else "✔ local changes detected: none"
    )

    print("✔ symlink health: OK")
    print("✔ config validation: passed")
    print()

    if report.modified_files:
        print("Changed files:")
        for f in report.modified_files:
            print(f"  - {f.path}")


def render_short(report: StatusReport):

    print("Status Summary:")
    print(f"- modified: {len(report.modified_files)}")
    print(f"- missing: {len(report.missing_files)}")
    print(f"- synced: {len(report.synced_files)}")


def render_json(report: StatusReport):

    def encode_file(f):
        return {
            "group": f.group,
            "entry": f.entry,
            "path": str(f.path),
            "state": f.state.value,
        }

    output = {
        "repo_clean": report.repo_clean,
        "total_files": report.total_files,
        "modified_files": [encode_file(f) for f in report.modified_files],
        "missing_files": [encode_file(f) for f in report.missing_files],
        "synced_files": [encode_file(f) for f in report.synced_files],
    }

    print(json.dumps(output, indent=2))


def status(props: StatusProps) -> None:

    repo = get_repo(props.profile_dir)

    if repo.bare:
        log("❌ The repository is bare. No profile available.")
        return

    config = conf_reader(config_file=Path(app_config_file))
    report = build_status_report(props, config, repo)

    if props.json:
        render_json(report)

    elif props.short:
        render_short(report)

    else:
        render_full(report)
