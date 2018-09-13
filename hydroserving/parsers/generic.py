from hydroserving.parsers.abstract import AbstractParser, UnknownResource
from hydroserving.parsers.application import ApplicationParser
from hydroserving.parsers.config import ConfigParser
from hydroserving.parsers.environment import EnvironmentParser
from hydroserving.parsers.model import ModelParser
from hydroserving.parsers.runtime import RuntimeParser


class GenericParser(AbstractParser):
    """
    Reads kind and version and chooses appropriate parser
    """

    def to_dict(self, obj):
        raise NotImplementedError()

    KIND_TO_PARSER = {
        "Config": ConfigParser(),
        "Model": ModelParser(),
        "Environment": EnvironmentParser(),
        "Runtime": RuntimeParser(),
        "Application": ApplicationParser()
    }

    def parse_dict(self, in_dict):
        kind = in_dict.get("kind")
        parser = GenericParser.KIND_TO_PARSER.get(kind)
        if parser is None:
            raise UnknownResource(None, kind)
        else:
            return parser.parse_dict(in_dict)
