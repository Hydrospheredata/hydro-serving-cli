from hydroserving.core.contract import contract_from_dict
from hydroserving.core.image import DockerImage
from hydroserving.core.model.entities import Model
from hydroserving.core.monitoring.parser import parse_monitoring_params


def parse_model(in_dict):
    if in_dict is None:
        return None
    contract = contract_from_dict(in_dict.get("contract"))
    model = Model(
        name=in_dict.get("name"),
        contract=contract,
        payload=in_dict.get("payload"),
        training_data_file=in_dict.get("training-data"),
        install_command=in_dict.get("install-command"),
        runtime=DockerImage.parse_fullname(in_dict["runtime"]),
        host_selector=in_dict.get("host-selector"),
        monitoring=parse_monitoring_params(in_dict.get("monitoring")),
        metadata=in_dict.get("metadata", {}),
    )
    model.validate()
    return model
