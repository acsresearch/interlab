import functools
import logging
from pathlib import Path
from typing import Any

import git  # installed with `pip install gitpython`
from hydra.experimental.callback import Callback
from omegaconf import DictConfig

logger = logging.getLogger(__name__)


def log_exceptions(logger: logging.Logger):
    """
    Decorator to catch and log exceptions.

    Useful in combination with hydra to make sure that also uncaught exceptions are properly logged to file.
    """

    def decorator(func):
        @functools.wraps(func)
        def decorated(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.exception(e)
                raise e

        return decorated

    return decorator


class LogGitHashCallback(Callback):
    """
    LogGitHashCallback logs, on the start of every run, the git hash of the current commit and changed files (if any).

    To use it include the following in your config:
        ```yaml
        hydra:
          callbacks:
            git_logging:
              _target_: interlab.utils.logs.LogGitHashCallback
        ```

    (adapted from https://stackoverflow.com/a/74133166)
    """

    def on_job_start(self, config: DictConfig, **kwargs: Any) -> None:
        _log_git_sha()


def _log_git_sha():
    log = logging.getLogger(__name__)

    repo = git.Repo(search_parent_directories=True)
    sha = repo.head.object.hexsha
    log.info(f"Git sha: {sha}")

    changed_files = [item.a_path for item in repo.index.diff(None)]
    if changed_files:
        log.info(f"Changed files: {changed_files}")

    diff = repo.git.diff()
    if diff:
        log.info(f"Git diff:\n{diff}")


class SymbolicLinkCallback(Callback):
    """
    SymbolicLinkCallback creates a symbolic link to all '.gz' files in Hydra's output directory in the parent directory.
    The '.gz' files are the gzipped log files created by the context and read by the server.
    This trick allows the server (which expects a flat directory structure) to find the log files.
    The callback runs at the end of every run.

    To use it include the following in your config:
        ```yaml
        hydra:
          callbacks:
            symlink:
              _target_: interlab.utils.logs.SymbolicLinkCallback
        ```
    """

    def on_job_end(self, config: DictConfig, **kwargs: Any) -> None:
        _create_symlinks()


def _create_symlinks():
    """
    Create symbolic links to all '.gz' files or '.ctx' directories in the current directory inside the parent directory.
    """
    logger.info("Creating symbolic links to log files and directories in parent directory")

    parent_dir = Path.cwd().parent
    for extension in ["gz", "ctx"]:
        for file_or_folder in Path.cwd().glob(f"*.{extension}"):
            symlink = parent_dir / file_or_folder.name
            if symlink.exists():
                logger.warning(f"Symlink {symlink} already exists, skipping")
                continue
            symlink.symlink_to(file_or_folder)
            logger.info(f"Created symlink {symlink} -> {file_or_folder}")
