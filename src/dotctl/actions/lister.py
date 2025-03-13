from pathlib import Path
from dataclasses import dataclass
from git import Repo, GitCommandError
from tabulate import tabulate
from dotctl.paths import app_profile_directory


@dataclass
class ListerProps:
    profile_dir: Path
    details: bool


lister_default_props = ListerProps(
    Path(app_profile_directory),
    details=False,
)


profile_meta = {
    "active": {
        "icon": "✅",
        "title": "Active",
        "desc": "Active Profile",
    },
    "not_active": {
        "icon": "➖",
        "title": "Inactive",
        "desc": "Inactive Profile",
    },
    "local_remote": {
        "icon": "",
        "title": "Synced",
        "desc": "Profile Synced with Cloud",
    },
    "local_only": {
        "icon": "󰟒",
        "title": "Self-Managed",
        "desc": "Locally managed profile available only on this machine",
    },
    "remote_only": {
        "icon": "",
        "title": "Cloud",
        "desc": "Other profile available on cloud, not on this machine",
    },
    "stale_remote": {
        "icon": "󰄛",
        "title": "Archived",
        "desc": "Previously available profile, may be outdated",
    },
    "behind_remote": {
        "icon": "󰯉",
        "title": "Update Available",
        "desc": "Newer version of this profile is available on cloud",
    },
    "ahead_remote": {
        "icon": "󰗡",
        "title": "Locally Updated",
        "desc": "This profile has local updates not yet synced",
    },
}


def get_profile_list(props: ListerProps):
    try:
        repo = Repo(props.profile_dir)

        if repo.bare:
            print("The repository is bare. No branches available.")
            return

        active_branch = repo.active_branch.name
        local_branches = {branch.name for branch in repo.branches}

        try:
            remote_branches = {
                ref.name.replace("origin/", "")
                for ref in repo.remotes.origin.refs
                if ref.name != "origin/HEAD"
            }
        except:
            remote_branches = set()

        branch_list = []
        for branch in local_branches | remote_branches | {active_branch}:
            is_active = (
                profile_meta["active"]["icon"]
                if branch == active_branch
                else profile_meta["not_active"]["icon"]
            )

            # Default profile
            profile_type = "local_only"

            # Determine profile type
            if branch in local_branches and branch in remote_branches:
                # Check if the branch is ahead/behind
                try:
                    ahead_behind = repo.git.rev_list(
                        f"origin/{branch}..{branch}", count=True
                    )
                    behind_ahead = repo.git.rev_list(
                        f"{branch}..origin/{branch}", count=True
                    )

                    if int(ahead_behind) > 0:
                        profile_type = "ahead_remote"  # Local is ahead
                    elif int(behind_ahead) > 0:
                        profile_type = "behind_remote"  # Local is behind
                    else:
                        profile_type = "local_remote"  # Synced
                except GitCommandError:
                    profile_type = "local_remote"  # Default to synced
            elif branch in remote_branches:
                profile_type = "remote_only"  # Remote Only (Cloud)
            elif branch in local_branches:
                # Check if it's a stale remote branch (deleted remotely)
                try:
                    repo.git.rev_list(f"origin/{branch}")
                except GitCommandError:
                    profile_type = "stale_remote"  # Stale Remote (Deleted Remotely)

            icon = profile_meta[profile_type]["icon"]
            title = profile_meta[profile_type]["title"]
            desc = profile_meta[profile_type]["desc"]

            profile_str = f"{is_active} {icon} {branch} ({title})"
            if props.details:
                profile_str = f"{profile_str}: {desc}"
            branch_list.append(profile_str)

        print("\n".join(branch_list))

    except GitCommandError as e:
        print(f"Git command error: {e}")
    except Exception as e:
        print(f"Error: {e}")
