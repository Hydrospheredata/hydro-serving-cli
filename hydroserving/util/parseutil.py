import logging
from typing import Callable, Any, Tuple
from hydrosdk.cluster import Cluster
from hydrosdk.builder import AbstractBuilder


def fill_arguments(partial_builder: Callable[[Any], AbstractBuilder], cluster: Cluster, **kwargs):
    return partial_builder(**kwargs).build(cluster, **kwargs)


def _parse_model_reference(reference: str) -> Tuple[str, int]:
    try: 
        name, version = reference.split(':')
        version = int(version)
    except ValueError as e:
        logging.error(f"Couldn't parse a model version reference string. "
            f"[NAME] argument should be in a form `name:version`. Actual: {reference}")
        raise SystemExit(1)
    return name, version