from typing import Callable, Any
from hydrosdk.cluster import Cluster
from hydrosdk.builder import AbstractBuilder


def fill_arguments(partial_builder: Callable[[Any], AbstractBuilder], cluster: Cluster, **kwargs):
    return partial_builder(**kwargs).build(cluster)