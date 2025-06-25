from dataclasses import dataclass
import socket
from datetime import datetime
from pathlib import Path
from dotctl.utils import log
from dotctl.handlers.data_handler import copy, delete
from dotctl.paths import app_profile_directory, app_config_file
from dotctl.handlers.config_handler import conf_reader
from dotctl.handlers.git_handler import (
    get_repo,
    get_repo_branches,
    git_fetch,
    pull_changes,
    checkout_branch,
    create_branch,
    is_repo_changed,
    add_changes,
    commit_changes,
    is_remote_repo,
    push_existing_branch,
    push_new_branch,
)
from dotctl.exception import exception_handler


@dataclass
class SaverProps:
    skip_sudo: bool
    password: str | None
    profile: str | None
    prune: bool


saver_default_props = SaverProps(
    skip_sudo=False,
    password=None,
    profile=None,
    prune=False,
)


@exception_handler
def save(props: SaverProps) -> None:
    log("Saving profile...")
    profile_dir = Path(app_profile_directory)
    profile = props.profile
    repo = get_repo(profile_dir)

    _, remote_profiles, active_profile, all_profiles = get_repo_branches(repo)
    if profile is not None and active_profile != profile:
        if profile not in all_profiles:
            git_fetch(repo)
            _, remote_profiles, active_profile, all_profiles = get_repo_branches(repo)
        if profile in all_profiles:
            checkout_branch(repo, profile)
            log(f"Switched to profile: {profile}")
        else:
            create_branch(repo=repo, branch=profile)
            log(f"Profile '{profile}' created and activated successfully.")
    if pull_changes(repo):
        log("Pulled latest changes from cloud successfully.")

    config = conf_reader(config_file=Path(app_config_file))

    for name, section in config.save.items():
        source_base_dir = Path(section.location)
        dest_base_dir = profile_dir / name
        dest_base_dir.mkdir(exist_ok=True)
        log(f'Saving "{name}"...')
        for entry in section.entries:
            source = source_base_dir / entry
            dest = dest_base_dir / entry
            result = copy(
                source,
                dest,
                skip_sudo=props.skip_sudo,
                sudo_pass=props.password,
                prune=props.prune,
            )

            # Updated props
            if result is not None:
                skip_sudo, sudo_pass = result
                if skip_sudo is not None:
                    props.skip_sudo = skip_sudo
                if sudo_pass is not None:
                    props.password = sudo_pass

    # Dots Config Cleanup
    if props.prune:
        dot_list = [
            p
            for p in profile_dir.iterdir()
            if p.is_dir() and p.name not in [".git", "hooks"]
        ]
        for dot in dot_list:
            if dot.name not in config.save.keys():
                log(f'Removing "{dot.name}"...')
                result = delete(
                    path=profile_dir / dot.name,
                    skip_sudo=props.skip_sudo,
                    sudo_pass=props.password,
                )
                # Updated props
                if result is not None:
                    skip_sudo, sudo_pass = result
                    if skip_sudo is not None:
                        props.skip_sudo = skip_sudo
                    if sudo_pass is not None:
                        props.password = sudo_pass
            else:
                entry_list = dot.iterdir()
                for entry in entry_list:
                    if entry.name not in config.save[dot.name].entries:
                        log(f'Removing "{dot.name}:{entry.name}"...')
                        result = delete(
                            path=profile_dir / dot.name / entry.name,
                            skip_sudo=props.skip_sudo,
                            sudo_pass=props.password,
                        )
                        # Updated props
                        if result is not None:
                            skip_sudo, sudo_pass = result
                            if skip_sudo is not None:
                                props.skip_sudo = skip_sudo
                            if sudo_pass is not None:
                                props.password = sudo_pass

    add_changes(repo=repo)
    if is_repo_changed(repo=repo):
        hostname = socket.gethostname()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_message = f"{hostname} | {timestamp}"
        commit_changes(repo=repo, message=full_message)
        is_remote, _ = is_remote_repo(repo=repo)
        profile = active_profile if not profile else profile
        if is_remote:
            if profile not in remote_profiles:
                git_fetch(repo=repo)
            if not profile in remote_profiles:
                push_new_branch(repo=repo)
            else:
                push_existing_branch(repo=repo)
        log("✅ Profile saved successfully!")
    else:
        log("ℹ️ No changes detected!")
