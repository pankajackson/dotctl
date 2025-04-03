import shutil
import socket
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
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


@exception_handler
def importer(props: ImporterProps) -> None:
    log("Importing profile...")
    if not props.profile:
        log("No profile specified")
        return

    profile_path = Path(props.profile)

    if not is_zipfile(profile_path):
        log("Invalid Profile file")
        return

    if profile_path.suffix != __EXPORT_EXTENSION__:
        log("Unsupported Profile file")
        return

    # Setup variables
    profile_dir = Path(app_profile_directory)
    repo = get_repo(profile_dir)
    profile_name = profile_path.stem
    temp_profile_dir = Path(app_home_directory) / profile_name

    # Create profile branch
    _, remote_profiles, active_profile, all_profiles = get_repo_branches(repo)
    if profile_name in all_profiles:
        log(f"Profile '{profile_name}' already exists")
        return

    create_branch(repo=repo, branch=profile_name)
    log(f"Profile '{profile_name}' created and activated successfully.")

    # Extract profile
    log("Extracting profile...")
    temp_profile_dir.mkdir(parents=True, exist_ok=True)

    with ZipFile(profile_path, "r") as zip_file:
        zip_file.extractall(temp_profile_dir)

    try:
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
            dest_base_dir.mkdir(parents=True, exist_ok=True)

            log(f'Importing "{name}"...')
            for entry in section.entries:
                source = source_base_dir / entry
                dest = dest_base_dir / entry
                result = copy(
                    source, dest, skip_sudo=props.skip_sudo, sudo_pass=props.password
                )

                # Updated props
                if result is not None:
                    skip_sudo, sudo_pass = result
                    if skip_sudo is not None:
                        props.skip_sudo = skip_sudo
                    if sudo_pass is not None:
                        props.password = sudo_pass

        # Cleanup extracted data after import
        shutil.rmtree(profile_dir / __EXPORT_DATA_DIR__)

        # Saving changes
        add_changes(repo=repo)
        hostname = socket.gethostname()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_message = f"{hostname} | Imported profile: {profile_name} | {timestamp}"
        commit_changes(repo=repo, message=full_message)

        is_remote, _ = is_remote_repo(repo=repo)
        if is_remote:
            push_new_branch(repo=repo)
        log("Profile Saved successfully!")

        checkout_branch(repo, active_profile)
        log(f"Switched back to profile: {active_profile}")

        log("Profile Imported successfully!")

    finally:
        shutil.rmtree(temp_profile_dir, ignore_errors=True)
