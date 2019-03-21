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
    clusters = in_dict['clusters']
    current_cluster = in_dict.get('current-cluster')
    if not current_cluster:  # back-compatible alternative
        current_cluster = in_dict['current_cluster']
    return ClusterConfig(current_cluster, clusters)
