from hydroserving.core.host_selector.host_selector import HostSelector
from hydroserving.core.parsers.abstract import AbstractParser


class HostSelectorParser(AbstractParser):
    def to_dict(self, obj):
        pass

    def parse_dict(self, in_dict):
        if in_dict is None:
            return None
        return HostSelector(
            name=in_dict.get("name"),
            selector=in_dict.get("selector")
        )
