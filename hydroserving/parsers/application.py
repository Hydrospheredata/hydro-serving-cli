from hydroserving.models.definitions.application import Application
from hydroserving.parsers.abstract import AbstractParser


class ApplicationParser(AbstractParser):
    def to_dict(self, obj):
        pass

    def parse_dict(self, in_dict):
        if in_dict is None:
            return None

        return Application(
            name=in_dict['name']
        )
