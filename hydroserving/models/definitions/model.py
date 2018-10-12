from hydro_serving_grpc import ModelContract


class Model:
    def __init__(self, name, model_type, contract, payload, description, training_data_file):
        """

        Args:
            name (str):
            model_type (str or None):
            contract (ModelContract or None):
            payload (list of str):
            description (str or None):
            training_data_file (str or None):
        """
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
        self.training_data_file = training_data_file
