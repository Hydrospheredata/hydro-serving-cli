from hydroserving.models.definitions.config import Config
from hydroserving.parsers.abstract import AbstractParser


class ConfigParser(AbstractParser):
    """
    Parser for configurations
    """

    def to_dict(self, obj):
        if not isinstance(obj, Config):
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
        return Config(current_cluster, clusters)
