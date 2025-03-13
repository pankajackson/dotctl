from pathlib import Path
from dotctl.paths import app_profile_directory
from git import Repo, GitCommandError
from tabulate import tabulate


ICONS = {
    "active": "✅",  # Active branch checkmark
    "inactive": "➖",  # Inactive branch dash
    "local_remote": "",  # Synced (Local & Remote)
    "local_only": "󰟒",  # Local Only (Self-Managed)
    "remote_only": "",  # Remote Only (Cloud)
    "stale_remote": "󰄛",  # Stale Remote (Old remote branch)
    "behind_remote": "󰯉",  # Local behind Remote
    "ahead_remote": "󰗡",  # Local ahead of Remote
}


def get_profile_list(profile_dir: Path = Path(app_profile_directory)):
    try:
        repo = Repo(profile_dir)

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
                ICONS["active"] if branch == active_branch else ICONS["inactive"]
            )

            # Determine icon based on branch status
            if branch in local_branches and branch in remote_branches:
                icon = ICONS["local_remote"]  # Synced (Local & Remote)
            elif branch in remote_branches:
                icon = ICONS["remote_only"]  # Remote Only (Cloud)
            else:
                icon = ICONS["local_only"]  # Local Only (Self-Managed)

            branch_list.append(f"{is_active} {icon} {branch}")

        print("\n".join(branch_list))

    except GitCommandError as e:
        print(f"Git command error: {e}")
    except Exception as e:
        print(f"Error: {e}")
