from hydroserving.models.definitions.config import Config
from hydroserving.parsers.abstract import AbstractParser


class ConfigParser(AbstractParser):
    """
    Parser for configurations
    """

    def parse_dict(self, in_dict):
        clusters = in_dict['clusters']
        return Config(clusters)
