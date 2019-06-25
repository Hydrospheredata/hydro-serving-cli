from hydroserving.core.host_selector.host_selector import HostSelector


def parse_host_selector(in_dict):
    if in_dict is None:
        return None
    return HostSelector(
        name=in_dict.get("name"),
        node_selector=in_dict.get("node_selector")
    )
