from hydro_serving_grpc import ModelContract

from hydroserving.core.model.service import InvalidModelException


class UploadMetadata:
    def __init__(self, name, contract, host_selector, runtime, install_command):
        self.contract = contract
        self.hostSelectorName = host_selector
        self.runtime = runtime
        self.name = name
        self.installCommand = install_command


class Model:
    def __init__(self, name, host_selector, runtime, contract, payload,
                 training_data_file, install_command):
        """
        Args:
            name (str):
            contract (ModelContract or None):
            payload (list of str):
            training_data_file (str or None):
        """
        self.name = name
        self.host_selector = host_selector
        self.runtime = runtime
        self.contract = contract
        self.payload = payload
        self.training_data_file = training_data_file
        self.install_command = install_command

    def validate(self):
        if not isinstance(self.name, str):
            raise InvalidModelException("name is not a string", self.__dict__)

        if self.runtime is None:
            raise InvalidModelException("runtime cannot be None", self.__dict__)

        if self.contract is not None and not isinstance(self.contract, ModelContract):
            raise InvalidModelException("contract is not a ModelContract", self.__dict__)

        if not isinstance(self.payload, list):
            raise InvalidModelException("payload is not a list", self.__dict__)

        if self.install_command is not None and not isinstance(self.install_command, str):
            raise InvalidModelException("install-command is not a string", self.__dict__)
