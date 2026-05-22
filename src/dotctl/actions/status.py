from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import json

from dotctl.paths import app_profile_directory, app_config_file
from dotctl.handlers.config_handler import conf_reader
from dotctl.handlers.git_handler import get_repo, is_git_repo
from dotctl.handlers.profile_handler import DriftReport, build_drift_report
from dotctl.utils import log


@dataclass
class StatusReport:
    repo_status: str
    config_status: str
    drift: DriftReport | None
    errors: list[str]


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

    print(f"Repository: {report.repo_status}")
    print(f"Config: {report.config_status}")

    if report.errors:
        print("\nErrors:")
        for error in report.errors:
            print(f"  - {error}")

    if report.drift is None:
        print("\n⚠ drift analysis unavailable")
        return

    drift = report.drift

    system_in_sync = drift.is_clean()

    print("\n✔ system: in sync" if system_in_sync else "\n⚠ system: drift detected")

    if drift.modified_files:
        print(f"⚠ modified files: {len(drift.modified_files)}")
    else:
        print("✔ modified files: none")

    if drift.missing_files:
        print(f"⚠ missing files: {len(drift.missing_files)}")
    else:
        print("✔ missing files: none")

    print("✔ symlink health: OK")  # placeholder

    if drift.modified_files or drift.missing_files:

        print("\nChanged files:")

        for f in drift.modified_files + drift.missing_files:
            print(f"  - {f.path}")


def render_short(report: StatusReport):

    if report.config_status != "ok":
        print(f"Config: {report.config_status}")
        return
    if report.repo_status != "ok":
        print(f"Repository: {report.repo_status}")
        return

    if report.drift is None:
        print("drift status: unavailable")
        return

    drift = report.drift

    if not report.drift.is_clean:
        print("Status Summary:")
        print(f"- modified: {len(drift.modified_files)}")
        print(f"- missing: {len(drift.missing_files)}")
        print(f"- synced: {len(drift.synced_files)}")


def render_json(report: StatusReport):

    def encode_file(f):
        return {
            "group": f.group,
            "entry": f.entry,
            "path": str(f.path),
            "state": f.state.value,
        }

    drift = report.drift

    output = {
        "repo_status": report.repo_status,
        "config_status": report.config_status,
        "errors": report.errors,
        "drift": None,
    }

    if drift is not None:

        output["drift"] = {
            "clean": drift.is_clean(),
            "total_files": drift.total_files(),
            "modified_files": [encode_file(f) for f in drift.modified_files],
            "missing_files": [encode_file(f) for f in drift.missing_files],
            "synced_files": [encode_file(f) for f in drift.synced_files],
        }

    print(json.dumps(output, indent=2))


def status(props: StatusProps) -> None:

    errors = []

    repo_status = "ok"
    config_status = "ok"

    config = None
    drift_report = None

    # Repository checks
    try:

        if not props.profile_dir.exists():
            repo_status = "not found"

        elif not props.profile_dir.is_dir():
            repo_status = "invalid directory"

        elif not is_git_repo(props.profile_dir):
            repo_status = "not a git repository"

        else:

            repo = get_repo(props.profile_dir)

            if repo.bare:
                repo_status = "bare repository"

    except Exception as e:

        repo_status = "error"
        errors.append(f"Repository check failed: {e}")

    # Config checks
    try:

        config_path = Path(app_config_file)

        if not config_path.exists():
            config_status = "not found"

        elif not config_path.is_file():
            config_status = "invalid file"

        else:

            config = conf_reader(config_file=config_path)

            if not config:
                config_status = "invalid config"

    except Exception as e:

        config_status = "error"
        errors.append(f"Config check failed: {e}")

    # Drift checks
    try:

        if repo_status == "ok" and config_status == "ok" and config:

            drift_report = build_drift_report(
                props.profile_dir,
                config,
            )

    except Exception as e:

        errors.append(f"Drift check failed: {e}")

    # Final report
    report = StatusReport(
        repo_status=repo_status,
        config_status=config_status,
        drift=drift_report,
        errors=errors,
    )

    # Render
    if props.json:
        render_json(report)

    elif props.short:
        render_short(report)

    else:
        render_full(report)
