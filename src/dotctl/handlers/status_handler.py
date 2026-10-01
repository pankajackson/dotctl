from enum import Enum
from dataclasses import dataclass, field
from pathlib import Path
import subprocess

from dotctl.handlers.config_handler import Config
from dotctl.handlers.diff_handler import get_file_diff
from dotctl.handlers.sudo_handler import path_exists


class StatusCode(Enum):

    # Generic

    OK = "ok"
    UNKNOWN = "unknown"
    ERROR = "error"

    # Repository

    REPO_NOT_FOUND = "repo_not_found"
    REPO_INVALID_DIRECTORY = "repo_invalid_directory"
    REPO_NOT_GIT = "repo_not_git"
    REPO_BARE = "repo_bare"
    REPO_REMOTE_UNAVAILABLE = "repo_remote_unavailable"
    REPO_FETCH_FAILED = "repo_fetch_failed"

    # Configuration

    CONFIG_NOT_FOUND = "config_not_found"
    CONFIG_INVALID_FILE = "config_invalid_file"
    CONFIG_PARSE_FAILED = "config_parse_failed"
    CONFIG_UNSUPPORTED = "config_unsupported"

    # Drift

    DRIFT_DETECTED = "drift_detected"
    DRIFT_ANALYSIS_FAILED = "drift_analysis_failed"
    DRIFT_CLEAN = "drift_clean"

    # File states

    FILE_MODIFIED = "file_modified"
    FILE_MISSING_SOURCE = "file_missing_source"
    FILE_MISSING_PROFILE = "file_missing_profile"

    # Future

    SYMLINK_BROKEN = "symlink_broken"
    HOOK_FAILED = "hook_failed"
    PERMISSION_DENIED = "permission_denied"


class Severity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


def status_icon(healthy: bool) -> str:
    return "✔" if healthy else "⚠"


class FileState(Enum):
    SYNCED = "synced"
    MODIFIED = "modified"
    MISSING_SOURCE = "missing_source"
    MISSING_PROFILE = "missing_profile"
    NOT_PRESENT = "not_present"
    INACCESSIBLE = "inaccessible"


@dataclass
class StatusEntry:
    group: str
    entry: str
    state: FileState
    path: Path


@dataclass
class DriftReport:
    modified_files: list[StatusEntry] = field(default_factory=list)
    missing_files: list[StatusEntry] = field(default_factory=list)
    synced_files: list[StatusEntry] = field(default_factory=list)
    not_present_files: list[StatusEntry] = field(default_factory=list)
    inaccessible_files: list[StatusEntry] = field(default_factory=list)

    def total_drift(self) -> int:
        return (
            len(self.modified_files)
            + len(self.missing_files)
            + len(self.inaccessible_files)
        )

    def total_files(self) -> int:
        return (
            len(self.modified_files)
            + len(self.missing_files)
            + len(self.synced_files)
            + len(self.not_present_files)
            + len(self.inaccessible_files)
        )

    def is_clean(self) -> bool:
        return self.total_drift() == 0


def get_file_state(
    source: Path, repo_file: Path, *, required_sudo: bool = False
) -> FileState:
    source_exists = _path_presence(source, required_sudo=required_sudo)
    repo_exists = _path_presence(repo_file)

    if source_exists is None or repo_exists is None:
        return FileState.INACCESSIBLE

    if not source_exists and repo_exists:
        return FileState.MISSING_SOURCE

    if source_exists and not repo_exists:
        return FileState.MISSING_PROFILE

    if not source_exists and not repo_exists:
        return FileState.NOT_PRESENT

    try:
        diff = get_file_diff(source, repo_file, required_sudo=required_sudo)
    except (PermissionError, subprocess.CalledProcessError):
        return FileState.INACCESSIBLE

    if diff:
        return FileState.MODIFIED

    return FileState.SYNCED


def _path_presence(path: Path, *, required_sudo: bool = False) -> bool | None:
    """Return presence including dangling symlinks, or None if inaccessible."""
    try:
        path.lstat()
        return True
    except FileNotFoundError:
        return False
    except PermissionError:
        try:
            return path_exists(path, required_sudo=required_sudo)
        except (PermissionError, subprocess.CalledProcessError):
            return None


def build_drift_report(profile_dir: Path, config: Config) -> DriftReport:

    results: list[StatusEntry] = []

    for name, section in config.save.items():

        for entry in section.entries:

            source = Path(section.location) / entry
            repo_file = profile_dir / name / entry

            state = get_file_state(
                source, repo_file, required_sudo=section.required_sudo
            )

            results.append(
                StatusEntry(
                    group=name,
                    entry=entry,
                    path=source,
                    state=state,
                )
            )

    modified = []
    missing = []
    synced = []
    not_present = []
    inaccessible = []

    for r in results:

        if r.state == FileState.MODIFIED:
            modified.append(r)

        elif r.state in (FileState.MISSING_SOURCE, FileState.MISSING_PROFILE):
            missing.append(r)

        elif r.state == FileState.NOT_PRESENT:
            not_present.append(r)

        elif r.state == FileState.INACCESSIBLE:
            inaccessible.append(r)

        else:
            synced.append(r)
    return DriftReport(
        modified_files=modified,
        missing_files=missing,
        synced_files=synced,
        not_present_files=not_present,
        inaccessible_files=inaccessible,
    )
