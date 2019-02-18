from hydroserving.core.monitoring.service import metric_spec_config_factory


def parse_monitoring_params(in_dict):
    """

    Args:
        in_dict (dict):

    Returns:
        MonitoringParams:
    """
    if in_dict is None:
        return None
    result = []
    for item in in_dict:
        result.append(
            {
                "name": item["name"],
                "withHealth": item["with-health"],
                "kind": item["kind"],
                "config": metric_spec_config_factory(item["kind"], **item["config"])
            }
        )
    return result
