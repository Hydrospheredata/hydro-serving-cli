from hydro_serving_grpc import ModelContract, ModelSignature, ModelField

from hydroserving.models.definitions.field import Field


class Model:
    def __init__(self, name, model_type, contract, payload, description):
        if not isinstance(name, str):
            raise TypeError("name is not a string", type(name))

        if model_type is not None and not isinstance(model_type, str):
            raise TypeError("model_type is not a string", type(model_type))

        if not isinstance(contract, ModelContract):
            raise TypeError("contract is not a ModelContract", type(contract))

        if not isinstance(payload, list):
            raise TypeError("payload is not a list", type(contract))

        if description is not None and not isinstance(description, str):
            raise TypeError("description is not a str", type(description))

        self.name = name
        self.model_type = model_type
        self.fields = contract
        self.payload = payload
        self.description = description

    @staticmethod
    def from_dict(data_dict):
        if data_dict is None:
            return None
        return Model(
            name=data_dict.get("name"),
            model_type=data_dict.get("type"),
            contract=Model.contract_from_dict(data_dict.get("contract")),
            payload=data_dict.get("payload"),
            description=data_dict.get("description")
        )

    @staticmethod
    def contract_from_dict(data_dict):
        if data_dict is None:
            return None
        signatures = []
        print(data_dict)
        for sig_name, value in data_dict.items():
            cur_sig = ModelSignature()
            inputs = []
            outputs = []
            # for in_key, in_value in value["inputs"]:
            #     inputs = ModelField(
            #         name=in_key,
            #         shape=
            #     )

        return signatures
