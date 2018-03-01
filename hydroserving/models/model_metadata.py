from hydroserving.helpers.contract import read_contract

class ModelMetadata:

    def __init__(self, model_name, model_type, model_contract, description):
        self.model_name = model_name
        self.model_type = model_type
        self.model_contract = model_contract
        self.description = description

    def to_upload_data(self):
        return {
            "model_name": self.model_name,
            "model_type": self.model_type,
            "model_contract": self.model_contract.SerializeToString(),
            "model_description": self.description,
        }

    @staticmethod
    def from_folder_metadata(model):
        return ModelMetadata(
            model_name=model.name,
            model_type=model.model_type,
            model_contract=read_contract(model),
            description=model.description
        )
