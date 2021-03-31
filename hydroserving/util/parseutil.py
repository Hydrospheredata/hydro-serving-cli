from typing import Callable, Any, Tuple
from hydrosdk.cluster import Cluster
from hydrosdk.builder import AbstractBuilder


def fill_arguments(partial_builder: Callable[[Any], AbstractBuilder], cluster: Cluster, **kwargs):
    return partial_builder(**kwargs).build(cluster)


def _parse_model_reference(reference: str) -> Tuple[str, int]:
    try: 
        name, version = reference.split(':')
        version = int(version)
    except ValueError as e:
        logging.error("Couldn't parse a model version reference string. "
            "[NAME] argument should be in a form `name:version`")
        raise SystemExit(1)
    return name, version