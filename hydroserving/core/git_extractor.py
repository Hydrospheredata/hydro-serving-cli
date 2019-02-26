import logging
from collections import namedtuple
import git

GitInfo = namedtuple("GitInfo", ["branch_name", "commit_sha", "is_dirty"])


def collect_git_info(path, search_parent_directories):
    try:
        repo = git.Repo(path, search_parent_directories=search_parent_directories)
        cur_branch = repo.active_branch
        cur_commit = cur_branch.commit
        cur_is_dirty = repo.is_dirty()
        meta = GitInfo(cur_branch.name, cur_commit.hexsha, cur_is_dirty)
        return meta
    except git.GitError as ex:
        logging.debug("Error while extracting .git metadata: %s", ex)
        return None
