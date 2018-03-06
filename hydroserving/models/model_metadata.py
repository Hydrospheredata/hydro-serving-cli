from hydroserving.helpers.contract import read_contract_cwd


class ModelMetadata:

    def __init__(self, model_name, model_type, model_contract, description):
        self.model_name = model_name
        self.model_type = model_type
        self.model_contract = model_contract
        self.description = description

    @staticmethod
    def from_folder_metadata(model):
        return ModelMetadata(
            model_name=model.name,
            model_type=model.model_type,
            model_contract=read_contract_cwd(model),
            description=model.description
        )
