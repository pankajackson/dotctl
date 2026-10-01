import shutil
import socket
import stat
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from pathlib import PurePosixPath
from zipfile import is_zipfile, ZipFile
from dotctl.utils import log
from dotctl.handlers.data_handler import copy
from dotctl.paths import app_profile_directory, app_home_directory, app_config_file
from dotctl.handlers.config_handler import conf_reader
from dotctl.handlers.git_handler import (
    commit_changes,
    get_repo,
    get_repo_branches,
    checkout_branch,
    create_branch,
    delete_local_branch,
    add_changes,
    is_remote_repo,
    push_new_branch,
)
from dotctl.exception import exception_handler
from dotctl import __EXPORT_EXTENSION__, __EXPORT_DATA_DIR__


@dataclass
class ImporterProps:
    profile: Path | None
    skip_sudo: bool
    password: str | None


importer_default_props = ImporterProps(
    profile=None,
    skip_sudo=False,
    password=None,
)


def _safe_extract(zip_file: ZipFile, destination: Path) -> None:
    """Extract an archive while rejecting traversal paths and symlinks."""
    root = destination.resolve()
    for member in zip_file.infolist():
        member_path = PurePosixPath(member.filename)
        if (
            member_path.is_absolute()
            or ".." in member_path.parts
            or "\\" in member.filename
        ):
            raise ValueError(f"Unsafe path in profile archive: {member.filename!r}")

        target = (root / Path(*member_path.parts)).resolve()
        if not target.is_relative_to(root):
            raise ValueError(f"Unsafe path in profile archive: {member.filename!r}")
        mode = member.external_attr >> 16
        if stat.S_ISLNK(mode):
            raise ValueError(
                f"Symlinks are not allowed in profile archives: {member.filename!r}"
            )

        if member.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue

        target.parent.mkdir(parents=True, exist_ok=True)
        with zip_file.open(member) as source, target.open("wb") as output:
            shutil.copyfileobj(source, output)


@exception_handler
def importer(props: ImporterProps) -> None:
    log("Importing profile...")
    if not props.profile:
        log("❌ No profile specified")
        return

    profile_path = Path(props.profile)

    if not is_zipfile(profile_path):
        log("❌ Invalid Profile file")
        return

    if profile_path.suffix != __EXPORT_EXTENSION__:
        log("❌ Unsupported Profile file")
        return

    # Setup variables
    profile_dir = Path(app_profile_directory)
    repo = get_repo(profile_dir)
    profile_name = profile_path.stem
    app_home = Path(app_home_directory)
    app_home.mkdir(parents=True, exist_ok=True)

    # Ensure the imported archive is safe before changing the active branch.
    _, _, active_profile, all_profiles = get_repo_branches(repo)
    if profile_name in all_profiles:
        log(f"❌ Profile '{profile_name}' already exists")
        return

    branch_created = False
    import_committed = False
    with tempfile.TemporaryDirectory(
        prefix="dotctl-import-", dir=app_home
    ) as temp_dir:
        temp_profile_dir = Path(temp_dir)
        try:
            log("Extracting profile...")
            with ZipFile(profile_path, "r") as zip_file:
                _safe_extract(zip_file, temp_profile_dir)

            create_branch(repo=repo, branch=profile_name)
            branch_created = True
            log(f"Profile '{profile_name}' created and activated successfully.")

            # Copy the profile
            copy(
                temp_profile_dir,
                profile_dir,
                skip_sudo=props.skip_sudo,
                sudo_pass=props.password,
            )

            # Read the config file
            config = conf_reader(config_file=Path(app_config_file))

            # Import "Exported Data"
            for name, section in config.export.items():
                source_base_dir = profile_dir / __EXPORT_DATA_DIR__ / name
                dest_base_dir = Path(section.location)

                log(f'Importing "{name}"...')
                for entry in section.entries:
                    source = source_base_dir / entry
                    dest = dest_base_dir / entry
                    result = copy(
                        source,
                        dest,
                        skip_sudo=props.skip_sudo,
                        sudo_pass=props.password,
                        sudo=section.sudo,
                    )

                # Updated props
                    if result is not None:
                        skip_sudo, sudo_pass = result
                        if skip_sudo is not None:
                            props.skip_sudo = skip_sudo
                        if sudo_pass is not None:
                            props.password = sudo_pass

            # Cleanup extracted data after import
            shutil.rmtree(profile_dir / __EXPORT_DATA_DIR__, ignore_errors=True)

            # Saving changes
            add_changes(repo=repo)
            hostname = socket.gethostname()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            full_message = f"{hostname} | Imported profile: {profile_name} | {timestamp}"
            commit_changes(repo=repo, message=full_message)
            import_committed = True

            is_remote, _ = is_remote_repo(repo=repo)
            if is_remote:
                push_new_branch(repo=repo)
            log("Profile Saved successfully!")

            log("✅ Profile Imported successfully!")
        finally:
            if branch_created:
                try:
                    if repo.active_branch.name != active_profile:
                        checkout_branch(repo, active_profile)
                        log(f"Switched back to profile: {active_profile}")
                    if not import_committed:
                        delete_local_branch(repo, profile_name)
                except Exception as error:
                    log(f"Failed to restore profile '{active_profile}': {error}")
