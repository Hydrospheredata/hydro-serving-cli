from hydroserving.core.monitoring_configuration.monitoring_configuration import MonitoringConfiguration


def parse_monitoring_configuration_selector(in_dict: dict):
    if in_dict is None:
        return None

    batch_size = in_dict.get("batch-size")

    if not batch_size:
        return None
    else:
        return MonitoringConfiguration(
            batch_size=batch_size
        )
