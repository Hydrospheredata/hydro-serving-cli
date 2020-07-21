from hydroserving.core.monitoring_configuration.monitoring_configuration import MonitoringConfiguration


def parse_monitoring_configuration_selector(in_dict: dict):
    if in_dict is None:
        return None
    return MonitoringConfiguration(
        batch_size=in_dict.get("batch_size")
    )
