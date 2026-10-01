from pathlib import Path
from difflib import unified_diff, SequenceMatcher
import os
from rich.console import Console
from rich.table import Table

console = Console()


def get_file_diff(source: Path, dest: Path) -> list[str] | None:
    if not _path_exists(source) and not _path_exists(dest):
        return None

    if source.is_symlink() or dest.is_symlink():
        return _get_single_file_diff(source, dest)

    # Configured entries may be directories. Compare their files by relative
    # path so additions and removals are reported as well as content changes.
    if (source.exists() and source.is_dir()) or (dest.exists() and dest.is_dir()):
        source_files = _directory_files(source)
        dest_files = _directory_files(dest)
        diffs: list[str] = []
        for relative_path in sorted(source_files.keys() | dest_files.keys()):
            source_file = (
                source_files[relative_path]
                if relative_path in source_files
                else source / relative_path
            )
            dest_file = (
                dest_files[relative_path]
                if relative_path in dest_files
                else dest / relative_path
            )
            file_diff = _get_single_file_diff(
                source_file,
                dest_file,
            )
            if file_diff:
                diffs.extend(file_diff)
        return diffs

    return _get_single_file_diff(source, dest)


def _directory_files(directory: Path) -> dict[Path, Path]:
    if not directory.is_dir():
        return {}
    return {
        path.relative_to(directory): path
        for path in directory.rglob("*")
        if path.is_file() or path.is_symlink()
    }


def _path_exists(path: Path) -> bool:
    try:
        path.lstat()
        return True
    except FileNotFoundError:
        return False


def _read_lines(path: Path, keepends: bool = True) -> list[str]:
    if path.is_symlink():
        suffix = "\n" if keepends else ""
        return [f"symlink -> {os.readlink(path)}{suffix}"]
    if path.is_file():
        return path.read_text().splitlines(keepends=keepends)
    return []


def _get_single_file_diff(source: Path, dest: Path) -> list[str] | None:
    if not _path_exists(source) and not _path_exists(dest):
        return None

    source_lines = _read_lines(source)
    dest_lines = _read_lines(dest)

    diff = list(
        unified_diff(
            dest_lines,
            source_lines,
            fromfile=str(dest),
            tofile=str(source),
        )
    )
    return diff


def is_target_match(
    target: Path | None,
    source: Path,
    repo_file: Path,
) -> bool:

    if target is None:
        return True

    try:
        target = target.resolve()
        source = source.resolve()
        repo_file = repo_file.resolve()

        return (
            source == target
            or repo_file == target
            or source in target.parents
            or repo_file in target.parents
            or target in source.parents
            or target in repo_file.parents
        )

    except Exception:
        return False


def render_colored_diff(lines: list[str]) -> None:

    for line in lines:

        line = line.rstrip("\n")

        if line.startswith("+++") or line.startswith("---"):
            console.print(line, style="yellow")

        elif line.startswith("@@"):
            console.print(line, style="cyan")

        elif line.startswith("+"):
            console.print(line, style="green")

        elif line.startswith("-"):
            console.print(line, style="red")

        else:
            console.print(line)


def render_side_by_side(source, dest):

    if (source.exists() and source.is_dir()) or (dest.exists() and dest.is_dir()):
        source_files = _directory_files(source)
        dest_files = _directory_files(dest)
        for relative_path in sorted(source_files.keys() | dest_files.keys()):
            source_file = (
                source_files[relative_path]
                if relative_path in source_files
                else source / relative_path
            )
            dest_file = (
                dest_files[relative_path]
                if relative_path in dest_files
                else dest / relative_path
            )
            if get_file_diff(source_file, dest_file):
                console.print(f"\n{relative_path}", style="bold")
                render_side_by_side(source_file, dest_file)
        return

    source_lines = _read_lines(source, keepends=False)
    dest_lines = _read_lines(dest, keepends=False)

    matcher = SequenceMatcher(None, dest_lines, source_lines)

    table = Table(show_lines=False)

    table.add_column("Repository", overflow="fold")
    table.add_column("Local", overflow="fold")

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():

        if tag == "equal":

            for left, right in zip(
                dest_lines[i1:i2],
                source_lines[j1:j2],
            ):
                table.add_row(left, right)

        elif tag == "replace":

            left_chunk = dest_lines[i1:i2]
            right_chunk = source_lines[j1:j2]

            max_len = max(len(left_chunk), len(right_chunk))

            for idx in range(max_len):

                left = left_chunk[idx] if idx < len(left_chunk) else ""
                right = right_chunk[idx] if idx < len(right_chunk) else ""

                table.add_row(
                    f"[red]{left}[/red]",
                    f"[green]{right}[/green]",
                )

        elif tag == "delete":

            for left in dest_lines[i1:i2]:
                table.add_row(
                    f"[red]{left}[/red]",
                    "",
                )

        elif tag == "insert":

            for right in source_lines[j1:j2]:
                table.add_row(
                    "",
                    f"[green]{right}[/green]",
                )

    console.print(table)
