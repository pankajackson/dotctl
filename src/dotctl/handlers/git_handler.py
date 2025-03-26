import sys
from git import Repo, InvalidGitRepositoryError
from pathlib import Path
from dotctl import __APP_NAME__, __DEFAULT_PROFILE__
from dotctl.utils import log


def is_git_repo(path: Path) -> bool:
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    dest = path.resolve()
    if dest is None:
        raise ValueError("Destination path cannot be None")
    try:
        Repo(path)
        return True
    except InvalidGitRepositoryError:
        return False
    except Exception as e:
        raise Exception(f"Unexpected error: {e}")


def clone_repo(git_url: str, dest: Path) -> Repo | None:
    if is_git_repo(dest):
        log(f"Profile already exists at {dest}")
        return
    repo = Repo.clone_from(git_url, dest)
    return repo


def create_local_repo(dest: Path) -> Repo | None:
    if is_git_repo(dest):
        log(f"Profile already exists at {dest}")
        return
    repo = Repo.init(dest)
    repo.git.checkout("-b", __DEFAULT_PROFILE__)
    repo.index.commit("Initial commit for dotctl")
    return repo
