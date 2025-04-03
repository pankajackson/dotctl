from dataclasses import dataclass
import shutil
from random import shuffle
from pathlib import Path
from dotctl.utils import log
from dotctl.handlers.data_handler import copy
from dotctl.paths import app_profile_directory, app_config_file, home_path
from dotctl.handlers.config_handler import conf_reader
from dotctl.handlers.git_handler import (
    get_repo,
    get_repo_branches,
    git_fetch,
    checkout_branch,
)
from dotctl.exception import exception_handler
from dotctl import __EXPORT_EXTENSION__, __EXPORT_DATA_DIR__


@dataclass
class ExporterProps:
    profile: str | None
    skip_sudo: bool
    password: str | None


exporter_default_props = ExporterProps(
    profile=None,
    skip_sudo=False,
    password=None,
)


@exception_handler
def exporter(props: ExporterProps) -> None:
    """Exports a dotfiles profile as a compressed archive."""
    log("Exporting profile...")

    profile_dir = Path(app_profile_directory)
    export_base_path = Path(home_path)
    repo = get_repo(profile_dir)

    _, remote_profiles, active_profile, all_profiles = get_repo_branches(repo)
    profile = props.profile or active_profile

    # Create export path directory with uniqueness
    export_profile_path = export_base_path / profile
    if (
        export_profile_path.exists()
        or export_profile_path.with_suffix(__EXPORT_EXTENSION__).exists()
    ):
        rand_chars = list("abcdefg12345")
        shuffle(rand_chars)
        rand_str = "".join(rand_chars)
        export_profile_path = export_base_path / f"{profile}_{rand_str}"
    export_profile_path.mkdir(parents=True, exist_ok=True)

    try:
        # Ensure the profile is active
        if profile != active_profile:
            if profile not in all_profiles:
                git_fetch(repo)
                _, remote_profiles, active_profile, all_profiles = get_repo_branches(
                    repo
                )

            if profile in all_profiles:
                checkout_branch(repo, profile)
                log(f"Switched to profile: {profile}")
            else:
                log(f"Profile '{profile}' not found.")
                return

        # Copy profile files
        copy(
            profile_dir,
            export_profile_path,
            skip_sudo=props.skip_sudo,
            sudo_pass=props.password,
        )

        # Read config file
        config = conf_reader(config_file=Path(app_config_file))
        export_data_path = export_profile_path / __EXPORT_DATA_DIR__

        for name, section in config.export.items():
            source_base_dir = Path(section.location)
            dest_base_dir = export_data_path / name
            dest_base_dir.mkdir(parents=True, exist_ok=True)

            log(f'Exporting "{name}"...')
            for entry in section.entries:
                source = source_base_dir / entry
                dest = dest_base_dir / entry
                result = copy(
                    source, dest, skip_sudo=props.skip_sudo, sudo_pass=props.password
                )

                # Update props based on the result
                if result is not None:
                    skip_sudo, sudo_pass = result
                    if skip_sudo is not None:
                        props.skip_sudo = skip_sudo
                    if sudo_pass is not None:
                        props.password = sudo_pass

        # Switch back to the original profile if changed
        if profile != active_profile:
            checkout_branch(repo, active_profile)
            log(f"Switched back to profile: {active_profile}")

        # Create archive and clean up
        log("Creating archive...")
        archive_file = shutil.make_archive(
            str(export_profile_path), "zip", root_dir=export_profile_path
        )

        shutil.move(archive_file, export_profile_path.with_suffix(__EXPORT_EXTENSION__))

        log(
            f"Successfully exported to {export_profile_path.with_suffix(__EXPORT_EXTENSION__)}"
        )
    finally:
        shutil.rmtree(export_profile_path, ignore_errors=True)
