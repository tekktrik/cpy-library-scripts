import functools
from typing import Tuple, Callable, Any, Optional
import git
import git.repo
import git.index.base
from cpy_scripts.lib_funcs import StrPath, LibFunc


def _get_repo_and_remote(
    lib_path: StrPath, remote_name: str = "origin"
) -> Tuple[git.repo.Repo, git.Remote]:

    # Create the repo and remote objects
    repo = git.repo.Repo(lib_path)
    remote = repo.remote(remote_name)

    return repo, remote


def sync_repo(
    lib_path: StrPath, remote_name: str = "origin", branch_name: str = "main"
) -> None:
    """
    Update the repo, and ensure it is on the given branch using a
    forced checkout

    :param StrPath lib_path: The path to the repo
    :param str remote_name: The remote name to fetch and pull,
        default is ``origin``
    :param str branch_name: The branch name to checkout, default
        is ``main``
    """

    # Create the repo and remote objects
    repo, remote = _get_repo_and_remote(lib_path, remote_name)

    # Fetch from the remote
    remote.fetch()

    # Checkout and pull to the given branchb
    # if repo.active_branch != branch_name:
    branch: git.Head = getattr(repo.heads, branch_name)
    branch.checkout(force=True)
    remote.pull()


def push_changes(lib_path: StrPath, remote_name: str = "origin") -> None:
    """
    Pushes any changes made to the repo to the given remote

    :param StrPath lib_path: The path to the repo
    :param str remote_name: (optional) The name of remote, default
        is ``main``
    """

    # Create the repo and remote objects
    _, remote = _get_repo_and_remote(lib_path, remote_name)

    # Push changes
    remote.push()


def commit_changes(
    lib_path: StrPath,
    message: str,
    remote_name: str = "origin",
    skip_hooks: bool = True,
) -> None:

    # Create the repo and remote objects
    repo, _ = _get_repo_and_remote(lib_path, remote_name)

    index_file = git.index.base.IndexFile(repo)
    index_file.add("*")
    index_file.commit(message, skip_hooks=skip_hooks)


def sync_commit_push(
    message: str,
    *,
    remote_name: str = "origin",
    branch_name: str = "main",
    skip_hooks: bool = True
):
    """
    Decorator for automatically fetching, pulling, and pushing changes
    for a library function

    :param str remote_name: (optional) The name of the remote, default
        is ``origin``
    :param str branch_name: (optional) The name of the branch, default
        is ``main``
    """

    def decorator_sync_commit_push(func):

        functools.wraps(func)

        def wrapper_sync_commit_push(lib_path: StrPath, *args, **kwargs) -> Any:

            # Fetch and pull to repo
            sync_repo(lib_path, remote_name, branch_name)

            # Run fucntion
            result = func(lib_path, *args, **kwargs)

            # Commit and push changes
            commit_changes(lib_path, message, remote_name, skip_hooks)
            push_changes(lib_path, remote_name)

            # Return the function result(s)
            return result

        return wrapper_sync_commit_push

    return decorator_sync_commit_push
