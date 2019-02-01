from hydroserving.helpers.contract import contract_from_dict
from hydroserving.models.definitions.model import Model
from hydroserving.parsers.abstract import AbstractParser


class ModelParser(AbstractParser):
    """
    Parses Model config.
    """

    def to_dict(self, obj):
        raise NotImplementedError()

    def parse_dict(self, in_dict):
        if in_dict is None:
            return None
        return Model(
            name=in_dict.get("name"),
            model_type=in_dict.get("model-type"),
            contract=contract_from_dict(in_dict.get("contract")),
            payload=in_dict.get("payload"),
            description=in_dict.get("description"),
            training_data_file=in_dict.get("training-data")
        )
