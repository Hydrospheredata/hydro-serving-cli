from hydroserving.config.cluster_config import ClusterConfig
from hydroserving.core.parsers.abstract import AbstractParser


class ConfigParser(AbstractParser):
    """
    Parser for configurations
    """

    def to_dict(self, obj):
        if not isinstance(obj, ClusterConfig):
            raise TypeError("obj is not a Config", obj)

        res = {
            'kind': "Config",
            'clusters': list(obj.clusters),
            'current-cluster': obj.current_cluster
        }
        return res

    def parse_dict(self, in_dict):
        clusters = in_dict['clusters']
        current_cluster = in_dict['current-cluster']
        return ClusterConfig(current_cluster, clusters)
