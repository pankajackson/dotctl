from pathlib import Path
from difflib import unified_diff, SequenceMatcher
from rich.console import Console
from rich.table import Table

console = Console()


def get_file_diff(source: Path, dest: Path) -> list[str] | None:
    if not source.exists() and not dest.exists():
        return None

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
        if path.is_file()
    }


def _get_single_file_diff(source: Path, dest: Path) -> list[str] | None:
    if not source.exists() and not dest.exists():
        return None

    source_lines = []
    dest_lines = []

    if source.exists() and source.is_file():
        source_lines = source.read_text().splitlines(keepends=True)

    if dest.exists() and dest.is_file():
        dest_lines = dest.read_text().splitlines(keepends=True)

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

        return source.resolve() == target or repo_file.resolve() == target

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

    source_lines = []
    dest_lines = []

    if source.exists() and source.is_file():
        source_lines = source.read_text().splitlines()

    if dest.exists() and dest.is_file():
        dest_lines = dest.read_text().splitlines()

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
