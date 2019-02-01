from hydroserving.core.parsers.abstract import AbstractParser, UnknownResource
from hydroserving.core.parsers.application import ApplicationParser
from hydroserving.core.parsers.config import ConfigParser
from hydroserving.core.parsers.environment import HostSelectorParser
from hydroserving.core.parsers.model import ModelParser


class GenericParser(AbstractParser):
    """
    Reads kind and version and chooses appropriate parser
    """

    KIND_TO_PARSER = {
        "Config": ConfigParser(),
        "Model": ModelParser(),
        "HostSelector": HostSelectorParser(),
        "Application": ApplicationParser()
    }

    def to_dict(self, obj):
        kind = obj.__class__.__name__
        parser = GenericParser.KIND_TO_PARSER.get(kind)
        if parser is None:
            raise UnknownResource(None, kind)
        else:
            return parser.to_dict(obj)

    def parse_dict(self, in_dict):
        kind = in_dict.get("kind")
        parser = GenericParser.KIND_TO_PARSER.get(kind)
        if parser is None:
            raise UnknownResource(None, kind)
        else:
            return parser.parse_dict(in_dict)
