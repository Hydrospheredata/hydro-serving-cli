from hydroserving.models.definitions.environment import Environment
from hydroserving.parsers.abstract import AbstractParser


class EnvironmentParser(AbstractParser):
    def to_dict(self, obj):
        pass

    def parse_dict(self, in_dict):
        if in_dict is None:
            return None
        return Environment(
            name=in_dict.get("name"),
            selector=in_dict.get("selector")
        )
