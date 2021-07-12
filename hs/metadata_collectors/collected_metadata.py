from typing import Optional
from pydantic import BaseModel
from hs.metadata_collectors.hs import HSInfo
from hs.metadata_collectors.dvc import DvcInfo
from hs.metadata_collectors.git import GitInfo

class CollectedMetadata(BaseModel):
    hs: HSInfo
    git: Optional[GitInfo]
    dvc: Optional[DvcInfo]

    @staticmethod
    def collect(path):
        git = GitInfo.collect(path)
        dvc = DvcInfo.collect(path)
        hs = HSInfo.collect()
        return CollectedMetadata(git = git, dvc = dvc, hs = hs)

    def to_metadata(self):
        d = self.hs.to_metadata()
        if self.git:
            d.update(self.git.to_metadata())
        if self.dvc:
            d.update(self.dvc.to_metadata())
        return d