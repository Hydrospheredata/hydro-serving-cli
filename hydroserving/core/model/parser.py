from click import ClickException

from hydroserving.core.contract import contract_from_dict
from hydroserving.core.image import DockerImage
from hydroserving.core.model.entities import Model
from hydroserving.core.monitoring.service import parse_monitoring_params
from hydroserving.core.monitoring_configuration.parser import parse_monitoring_configuration_selector


def parse_model(in_dict: dict):
    if in_dict is None:
        return None
    contract = contract_from_dict(in_dict.get("contract"))
    if not in_dict['runtime']:
        raise ClickException("'runtime' field is not defined")
    monitoring_configuration = in_dict.get("monitoring-configuration")

    model = Model(
        name=in_dict.get("name"),
        contract=contract,
        payload=in_dict.get("payload"),
        training_data_file=in_dict.get("training-data"),
        install_command=in_dict.get("install-command"),
        runtime=DockerImage.parse_fullname(in_dict["runtime"]),
        monitoring=parse_monitoring_params(in_dict.get("monitoring")),
        metadata=parse_metadata(in_dict.get("metadata")),
        monitoring_configuration=parse_monitoring_configuration_selector(monitoring_configuration)
    )
    model.validate()

    return model


def parse_metadata(in_dict):
    if in_dict is None:
        return {}
    res = {}
    for key, val in in_dict.items():
        if not isinstance(val, str):
            res[key] = str(val)
        else:
            res[key] = val
    return res
