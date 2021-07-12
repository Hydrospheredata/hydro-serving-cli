import os
from hs.entities.base_entity import BaseEntity
from click.exceptions import ClickException
from pydantic import AnyHttpUrl
from typing import List
from hydrosdk.cluster import Cluster
from hs.settings import CONFIG_PATH

class ClusterServerDef(BaseEntity):
    server: AnyHttpUrl

class ClusterDef(BaseEntity):
    name: str
    cluster: ClusterServerDef

class ClusterConfig(BaseEntity):
    current_cluster: str
    clusters: List[ClusterDef]

def read_cluster_config(path: str) -> ClusterConfig:
    try:
        return ClusterConfig.parse_file(path)
    except FileNotFoundError:
        return None

def read_current_cluster(path: str) -> ClusterDef:
    config = read_cluster_config(path)
    if config is not None:
        for cl in config.clusters:
            if cl.name == config.current_cluster:
                return cl
    return None

def write_cluster_config(path: str, cluster_config: ClusterConfig):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        d = cluster_config.yaml()
        f.write(d)

def get_cluster_connection(path: str = CONFIG_PATH) -> Cluster:
    current_cluster = read_current_cluster(path)
    if current_cluster is None:
        raise ClickException("Can't establish connection to Hydrosphere cluster: cluster config is missing. Use `hs cluster` commands.")
    return Cluster(http_address=current_cluster.cluster.server)