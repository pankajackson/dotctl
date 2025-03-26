from git import Repo, InvalidGitRepositoryError, GitCommandError
from pathlib import Path
from dotctl import __APP_NAME__, __DEFAULT_PROFILE__
from dotctl.utils import log


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
