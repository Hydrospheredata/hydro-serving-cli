from hydroserving.parsers.abstract import AbstractParser
from hydroserving.parsers.config import ConfigParser
from hydroserving.parsers.model import ModelParser


class GenericParser(AbstractParser):
    """
    Reads kind and version and chooses appropriate parser
    """

    def to_dict(self, obj):
        raise NotImplementedError()

    KIND_TO_PARSER = {
        "Config": ConfigParser(),
        "Model": ModelParser()
    }

    def parse_dict(self, in_dict):
        kind = in_dict.get("kind")
        parser = GenericParser.KIND_TO_PARSER.get(kind)
        if parser is None:
            return None
        else:
            return parser.parse_dict(in_dict)
