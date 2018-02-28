class Model:
    def __init__(self, name, model_type, contract_path, payload):
        self.name = name
        self.model_type = model_type
        self.contract_path = contract_path
        self.payload = payload

    @staticmethod
    def from_dict(data_dict):
        if data_dict is None:
            return None
        return Model(
            name=data_dict.get("name"),
            model_type=data_dict.get("type"),
            contract_path=data_dict.get("contract"),
            payload=data_dict.get("payload")
        )