import logging
from typing import Any, Optional
from pydantic import BaseModel

class DvcInfo(BaseModel):
    metrics: Any

    def to_metadata(self):
        d = {}
        for k, v in self.metrics.items():
            metric_name = "dvc.metrics/"+k
            d[metric_name] = v
        return d

    @staticmethod
    def collect(path) -> Optional["DvcInfo"]:
        try:
            from dvc.repo import Repo
            repo = Repo(path)
            all_metrics = repo.metrics.show()
            cur_metrics = all_metrics['']  # get metrics for current branch
            return DvcInfo(cur_metrics)
        except Exception as ex:
            logging.debug("Can't extract DVC metadata", exc_info=True)
            return None
