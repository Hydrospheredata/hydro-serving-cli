class ModelDefinition:
    def __init__(self, name, model_type, contract_path, payload, description):
        self.name = name
        self.model_type = model_type
        self.contract_path = contract_path
        self.payload = payload
        self.description = description

    @staticmethod
    def from_dict(data_dict):
        if data_dict is None:
            return None
        return ModelDefinition(
            name=data_dict.get("name"),
            model_type=data_dict.get("type"),
            contract_path=data_dict.get("contract"),
            payload=data_dict.get("payload"),
            description=data_dict.get("description")
        )
