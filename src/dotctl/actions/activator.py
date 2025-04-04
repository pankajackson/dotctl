from pathlib import Path
from dataclasses import dataclass
from dotctl.utils import log
from dotctl.handlers.data_handler import copy
from dotctl.paths import app_profile_directory, app_config_file
from dotctl.handlers.config_handler import conf_reader
from dotctl.handlers.hooks_handler import run_hooks
from dotctl.handlers.git_handler import (
    get_repo,
    get_repo_branches,
    git_fetch,
    checkout_branch,
)
from dotctl.exception import exception_handler


@dataclass
class ActivatorProps:
    skip_sudo: bool
    password: str | None
    profile: str | None
    skip_hooks: bool
    skip_pre_hooks: bool
    skip_post_hooks: bool
    ignore_hook_errors: bool


activator_default_props = ActivatorProps(
    skip_sudo=False,
    password=None,
    profile=None,
    skip_hooks=False,
    skip_pre_hooks=False,
    skip_post_hooks=False,
    ignore_hook_errors=False,
)


@exception_handler
def apply(props: ActivatorProps) -> None:
    log("Activating profile...")
    profile_dir = Path(app_profile_directory)
    profile = props.profile
    repo = get_repo(profile_dir)

    _, _, active_profile, all_profiles = get_repo_branches(repo)
    if profile is not None and active_profile != profile:
        if profile not in all_profiles:
            git_fetch(repo)
        if profile in all_profiles:
            checkout_branch(repo, profile)
            log(f"Switched to profile: {profile}")
        else:
            log(f"Profile {profile} is not available.")
            return

    config = conf_reader(config_file=Path(app_config_file))
    if not props.skip_hooks and not props.skip_pre_hooks:
        run_hooks(pre_apply_hooks=True, ignore_errors=props.ignore_hook_errors)

    for name, section in config.save.items():
        source_base_dir = profile_dir / name
        dest_base_dir = Path(section.location)
        dest_base_dir.mkdir(exist_ok=True)
        log(f'Applying "{name}"...')
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

    if not props.skip_hooks and not props.skip_post_hooks:
        run_hooks(post_apply_hooks=True, ignore_errors=props.ignore_hook_errors)
    log("Profile saved successfully!")
