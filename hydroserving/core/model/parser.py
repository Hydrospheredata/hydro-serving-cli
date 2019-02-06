from hydroserving.core.contract import contract_from_dict
from hydroserving.core.image import DockerImage
from hydroserving.core.model.entities import Model
from hydroserving.core.parsers.abstract import AbstractParser


class ModelParser(AbstractParser):
    """
    Parses Model config.
    """

    def to_dict(self, obj):
        raise NotImplementedError()

    def parse_dict(self, in_dict):
        if in_dict is None:
            return None
        model = Model(
            name=in_dict.get("name"),
            contract=contract_from_dict(in_dict.get("contract")),
            payload=in_dict.get("payload"),
            training_data_file=in_dict.get("training-data"),
            install_command=in_dict.get("install-command"),
            runtime=DockerImage.parse_fullname(in_dict["runtime"]),
            host_selector=in_dict.get("host-selector")
        )
        model.validate()
        return model
