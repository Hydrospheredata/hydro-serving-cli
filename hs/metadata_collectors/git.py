import logging
from sys import exc_info
import time
from typing import Optional
from pydantic import BaseModel

class GitInfo(BaseModel):
    branch_name: str
    commit_sha: str
    is_dirty: bool
    author_name: str 
    author_email: str
    date: str

    def to_metadata(self):
        return {'git.branch': self.branch_name,
         'git.branch.head.sha': self.commit_sha,
         'git.branch.head.author.name': self.author_name,
         'git.branch.head.author.email': self.author_email,
         'git.branch.head.date': self.date,
         'git.is-dirty': str(self.is_dirty)}

    @staticmethod
    def collect(path) -> Optional["GitInfo"]:
        try:
            import git
            repo = git.Repo(path, search_parent_directories=True)
            cur_branch = repo.active_branch
            cur_commit = cur_branch.commit
            author = cur_commit.author
            date = time.asctime(time.gmtime(cur_commit.committed_date))
            cur_is_dirty = repo.is_dirty()
            meta = GitInfo(cur_branch.name, cur_commit.hexsha, cur_is_dirty, author.name, author.email, date)
            return meta
        except Exception:
            logging.debug("Error while extracting .git metadata", exc_info=True)
            return None

