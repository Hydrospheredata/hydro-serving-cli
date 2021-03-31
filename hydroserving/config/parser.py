from hydroserving.config.cluster_config import ClusterConfig


def config_to_dict(obj):
    if not isinstance(obj, ClusterConfig):
        raise TypeError("obj is not a Config", obj)

    res = {
        'kind': "Config",
        'clusters': list(obj.clusters),
        'current-cluster': obj.current_cluster
    }
    return res


def parse_config(in_dict):
    clusters = in_dict.get('clusters', [])
    current_cluster = in_dict.get('current-cluster', None)
    if current_cluster is None:
        current_cluster = in_dict.get('current_cluster', None)
    return ClusterConfig(current_cluster, clusters)
