from enum import Enum
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import json

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
class StatusReport:
    repo_clean: bool
    total_files: int
    modified_files: list[StatusEntry]
    missing_files: list[StatusEntry]
    synced_files: list[StatusEntry]


def get_state(source: Path, repo_file: Path) -> FileState:

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


def build_status_report(props, config, repo) -> StatusReport:

    results: list[StatusEntry] = []

    for name, section in config.save.items():

        for entry in section.entries:

            source = Path(section.location) / entry
            repo_file = props.profile_dir / name / entry

            state = get_state(source, repo_file)

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

    return StatusReport(
        repo_clean=repo_clean,
        total_files=len(results),
        modified_files=modified,
        missing_files=missing,
        synced_files=synced,
    )
