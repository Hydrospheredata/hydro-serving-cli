import logging
from collections import namedtuple

DvcInfo = namedtuple("DvcInfo", ["metrics"])


def collect_dvc_info(path):
    try:
        from dvc.repo import Repo
        repo = Repo(path)
        all_metrics = repo.metrics.show()
        cur_metrics = all_metrics['']  # get metrics for current branch
        return DvcInfo(cur_metrics)
    except Exception as ex:
        logging.debug("Can't extract DVC metadata: %s", ex)
        return None


def dvc_to_dict(dvc_info):
    d = {}
    for k, v in dvc_info.metrics.items():
        metric_name = "dvc.metrics/"+k
        d[metric_name] = v
    return d
