from pathlib import Path
from dataclasses import dataclass
from dotctl.utils import log
from dotctl.handlers.data_handler import copy
from dotctl.paths import app_profile_directory, app_config_file
from dotctl.handlers.config_handler import conf_reader
from dotctl.handlers.git_handler import (
    get_repo,
    get_repo_branches,
    git_fetch,
    checkout_branch,
    create_branch,
)
from dotctl.exception import exception_handler


@dataclass
class SaverProps:
    skip_sudo: bool
    password: str | None
    profile: str | None


saver_default_props = SaverProps(
    skip_sudo=False,
    password=None,
    profile=None,
)


@exception_handler
def save(props: SaverProps) -> None:
    log("Saving profile...")
    profile_dir = Path(app_profile_directory)
    profile = props.profile
    repo = get_repo(profile_dir)

    _, _, _, all_profiles = get_repo_branches(repo)
    if profile is not None:
        if profile not in all_profiles:
            git_fetch(repo)
        if profile in all_profiles:
            checkout_branch(repo, profile)
        else:
            create_branch(repo=repo, branch=profile)

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
                source, dest, skip_sudo=props.skip_sudo, sudo_pass=props.password
            )

            # Updated props
            if result is not None:
                skip_sudo, sudo_pass = result
                if skip_sudo is not None:
                    props.skip_sudo = skip_sudo
                if sudo_pass is not None:
                    props.password = sudo_pass

    log("Profile saved successfully!")
