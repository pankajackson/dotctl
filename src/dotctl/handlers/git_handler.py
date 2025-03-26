from dataclasses import dataclass
from pathlib import Path
import getpass
from git import Repo, InvalidGitRepositoryError, GitCommandError
from dotctl import __APP_NAME__, __DEFAULT_PROFILE__
from dotctl.utils import log


@dataclass
class RepoMetaData:
    repo_name: str
    owner: str
    last_commit_author: str


def is_git_repo(path: Path) -> bool:
    if not path.exists() or not path.is_dir():
        return False
    dest = path.resolve()
    if dest is None:
        return False
    try:
        Repo(path)
        return True
    except InvalidGitRepositoryError:
        return False
    except Exception as e:
        raise Exception(f"Unexpected error: {e}")


def get_repo(path: Path) -> Repo:
    if not is_git_repo(path):
        raise Exception(
            f"Profile not yet initialized, run `{__APP_NAME__} init` first."
        )
    return Repo(path)


def git_fetch(repo: Repo) -> None:
    try:
        if repo.remotes:
            origin = next(
                (remote for remote in repo.remotes if remote.name == "origin"),
                None,
            )
            if origin:
                origin.fetch(prune=True)
    except Exception as e:
        log(f"Failed to fetch remote: {e}")


def clone_repo(git_url: str, dest: Path) -> Repo | None:
    if is_git_repo(dest):
        log(f"Profile already exists")
        return
    try:
        repo = Repo.clone_from(git_url, dest)
        return repo
    except Exception as e:
        raise Exception(f"Failed to clone repo from {git_url} to {dest}. {e}")


def create_local_repo(dest: Path) -> Repo | None:
    if is_git_repo(dest):
        log(f"Profile already exists")
        return
    dest.mkdir(parents=True, exist_ok=True)
    repo = Repo.init(dest)
    repo.git.checkout("-b", __DEFAULT_PROFILE__)
    repo.index.commit("Initial commit for dotctl")
    return repo


def get_repo_branches(repo: Repo):
    active_profile = repo.active_branch.name
    local_profiles = {profile.name for profile in repo.branches}

    try:
        remote_profiles = set()
        if repo.remotes:
            try:
                origin = next(
                    (remote for remote in repo.remotes if remote.name == "origin"),
                    None,
                )
                if origin:
                    remote_profiles = {
                        ref.name.replace("origin/", "")
                        for ref in origin.refs
                        if ref.name != "origin/HEAD"
                    }
            except GitCommandError:
                remote_profiles = set()
    except GitCommandError:
        remote_profiles = set()

    all_profiles = local_profiles | remote_profiles | {active_profile}
    return local_profiles, remote_profiles, active_profile, all_profiles


def create_branch(repo: Repo, branch: str) -> None:
    if repo.bare:
        raise Exception("Error: The repository is bare. Cannot create a branch.")
    has_commits = repo.head.is_valid() if repo.head else False
    if not has_commits:
        repo.index.commit("Initial commit for dotctl")
    new_branch = repo.create_head(branch)
    new_branch.checkout()


def checkout_branch(repo: Repo, branch: str) -> None:
    repo.git.checkout(branch)


def delete_local_branch(repo: Repo, branch: str) -> None:

    # If trying to delete the active branch, checkout to another first
    if repo.active_branch.name == branch:
        fallback_branch = next(
            (b.name for b in repo.branches if b.name != branch), None
        )
        if fallback_branch:
            repo.git.checkout(fallback_branch)
        else:
            raise Exception("No fallback branch available to checkout before deletion.")
    repo.delete_head(branch, force=True)


def delete_remote_branch(repo: Repo, branch: str) -> None:
    try:
        origin = repo.remotes.origin if "origin" in repo.remotes else None
        if origin:
            origin.push(refspec=f":refs/heads/{branch}")
        else:
            log("No remote 'origin' found to delete the remote profile.")
    except GitCommandError as e:
        log(f"Failed to delete remote branch '{branch}': {e}")


def get_repo_meta(repo: Repo) -> RepoMetaData:

    if repo.bare:
        return RepoMetaData(
            repo_name="bare_repo",
            owner=getpass.getuser(),
            last_commit_author="No commits",
        )

    remote_url = repo.remotes.origin.url if repo.remotes else "No remote"

    try:
        last_commit = repo.head.commit
        last_commit_author = last_commit.author.name or "Unknown"
    except ValueError:  # Handles empty repos (no commits yet)
        last_commit_author = "No commits"

    if remote_url != "No remote":
        if remote_url.startswith("git@"):
            repo_name = remote_url.split(":")[-1].replace(".git", "")
            owner = remote_url.split(":")[-1].split("/")[0]
        else:
            repo_name = remote_url.split("/")[-1].replace(".git", "")
            owner = remote_url.split("/")[-2]
    else:
        repo_name = (
            Path(repo.working_tree_dir).name if repo.working_tree_dir else "unknown"
        )
        owner = (
            last_commit_author
            if last_commit_author != "No commits"
            else getpass.getuser()
        )

    return RepoMetaData(
        repo_name=repo_name,
        owner=owner,
        last_commit_author=last_commit_author,
    )
