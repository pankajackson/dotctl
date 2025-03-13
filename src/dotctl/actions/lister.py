from pathlib import Path
from dotctl.paths import app_profile_directory
from git import Repo, GitCommandError
from tabulate import tabulate


ICONS = {
    "active_local_remote": " 󰸞",  # Active branch (exists locally & remotely)
    "active_local_only": "󰟒 󰸞",  # Active branch (only local)
    "local_remote": "",  # Exists both locally & remotely
    "local_only": "󰟒",  # Only local
    "remote_only": "",  # Only remote
}


def get_profile_list(profile_dir: Path = Path(app_profile_directory)):
    try:
        repo = Repo(profile_dir)

        if repo.bare:
            print("The repository is bare. No branches available.")
            return

        # Get active branch
        active_branch = repo.active_branch.name

        # Get local branches
        local_branches = {branch.name for branch in repo.branches}

        # Get remote branches (excluding origin/HEAD)
        try:
            remote_branches = {
                ref.name.replace("origin/", "")
                for ref in repo.remotes.origin.refs
                if ref.name != "origin/HEAD"
            }
        except:
            remote_branches = set()

        # Create branch status mapping with icons
        branch_table = []
        for branch in (
            local_branches | remote_branches | {active_branch}
        ):  # Union of both sets
            if branch == active_branch:
                status = (
                    f"{ICONS['active_local_remote']} Active (Local & Remote)"
                    if branch in remote_branches
                    else f"{ICONS['active_local_only']} Active (Local Only)"
                )
            elif branch in local_branches and branch in remote_branches:
                status = f"{ICONS['local_remote']} Local & Remote"
            elif branch in local_branches:
                status = f"{ICONS['local_only']} Local Only"
            else:  # Only in remote
                status = f"{ICONS['remote_only']} Remote Only"

            branch_table.append([branch, status])

        # Print table with emojis
        print(
            tabulate(
                branch_table, headers=["Profile", "Status"], tablefmt="heavy_grid"
            )
        )

    except GitCommandError as e:
        print(f"Git command error: {e}")
    except Exception as e:
        print(f"Error: {e}")
