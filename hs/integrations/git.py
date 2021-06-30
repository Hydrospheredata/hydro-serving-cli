import logging
import time
from collections import namedtuple

GitInfo = namedtuple("GitInfo", ["branch_name", "commit_sha", "is_dirty", "author_name", "author_email", "date"])


def collect_git_info(path, search_parent_directories):
    try:
        import git
        repo = git.Repo(path, search_parent_directories=search_parent_directories)
        cur_branch = repo.active_branch
        cur_commit = cur_branch.commit
        author = cur_commit.author
        date = time.asctime(time.gmtime(cur_commit.committed_date))
        cur_is_dirty = repo.is_dirty()
        meta = GitInfo(cur_branch.name, cur_commit.hexsha, cur_is_dirty, author.name, author.email, date)
        return meta
    except Exception as ex:
        logging.debug("Error while extracting .git metadata: %s", ex)
        return None


def git_to_dict(gitinfo):
    d = {'git.branch': gitinfo.branch_name,
         'git.branch.head.sha': gitinfo.commit_sha,
         'git.branch.head.author.name': gitinfo.author_name,
         'git.branch.head.author.email': gitinfo.author_email,
         'git.branch.head.date': gitinfo.date,
         'git.is-dirty': str(gitinfo.is_dirty)}
    return d
