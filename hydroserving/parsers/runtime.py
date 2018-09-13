from hydroserving.models.definitions.runtime import Runtime
from hydroserving.parsers.abstract import AbstractParser


class RuntimeParser(AbstractParser):
    def to_dict(self, obj):
        pass

    def parse_dict(self, in_dict):
        if in_dict is None:
            return None
        return Runtime(
            name=in_dict.get("name"),
            version=in_dict.get("version"),
            model_type=in_dict.get("model-type"),
            tags=[],
            config_params={})
