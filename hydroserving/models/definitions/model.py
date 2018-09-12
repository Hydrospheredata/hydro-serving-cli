from hydro_serving_grpc import ModelContract

from hydroserving.helpers.contract import contract_from_dict


class Model:
    def __init__(self, name, model_type, contract, payload, description):
        if not isinstance(name, str):
            raise TypeError("name is not a string", type(name))

        if model_type is not None and not isinstance(model_type, str):
            raise TypeError("model_type is not a string", type(model_type))

        if contract is not None and not isinstance(contract, ModelContract):
            raise TypeError("contract is not a ModelContract", type(contract))

        if not isinstance(payload, list):
            raise TypeError("payload is not a list", type(contract))

        if description is not None and not isinstance(description, str):
            raise TypeError("description is not a str", type(description))

        self.name = name
        self.model_type = model_type
        self.contract = contract
        self.payload = payload
        self.description = description

    @staticmethod
    def from_dict(data_dict):
        if data_dict is None:
            return None
        return Model(
            name=data_dict.get("name"),
            model_type=data_dict.get("model-type"),
            contract=contract_from_dict(data_dict.get("contract")),
            payload=data_dict.get("payload"),
            description=data_dict.get("description")
        )
