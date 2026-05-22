from enum import Enum
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
import json

from dotctl.handlers.config_handler import Config
from dotctl.handlers.diff_handler import get_file_diff


class FileState(Enum):
    SYNCED = "synced"
    MODIFIED = "modified"
    MISSING_SOURCE = "missing_source"
    MISSING_REPO = "missing_repo"


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

    def total_drift(self) -> int:
        return len(self.modified_files) + len(self.missing_files)

    def total_files(self) -> int:
        return (
            len(self.modified_files) + len(self.missing_files) + len(self.synced_files)
        )

    def is_clean(self) -> bool:
        return self.total_drift() == 0


def get_file_state(source: Path, repo_file: Path) -> FileState:

    source_exists = source.exists()
    repo_exists = repo_file.exists()

    if not source_exists and repo_exists:
        return FileState.MISSING_SOURCE

    if source_exists and not repo_exists:
        return FileState.MISSING_REPO

    if not source_exists and not repo_exists:
        return FileState.SYNCED  # edge case safe ignore

    diff = get_file_diff(source, repo_file)

    if diff:
        return FileState.MODIFIED

    return FileState.SYNCED


def build_drift_report(profile_dir: Path, config: Config) -> DriftReport:

    results: list[StatusEntry] = []

    for name, section in config.save.items():

        for entry in section.entries:

            source = Path(section.location) / entry
            repo_file = profile_dir / name / entry

            state = get_file_state(source, repo_file)

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

    for r in results:

        if r.state == FileState.MODIFIED:
            modified.append(r)

        elif r.state in (FileState.MISSING_SOURCE, FileState.MISSING_REPO):
            missing.append(r)

        else:
            synced.append(r)
    repo_clean = len(modified) == 0 and len(missing) == 0

    return DriftReport(
        modified_files=modified,
        missing_files=missing,
        synced_files=synced,
    )
