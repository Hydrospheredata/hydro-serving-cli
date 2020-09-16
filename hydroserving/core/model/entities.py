from enum import Enum

from hydro_serving_grpc.contract import ModelContract

from hydroserving.core.image import DockerImage
from hydroserving.core.monitoring_configuration.monitoring_configuration import MonitoringConfiguration


class VersionStatus(Enum):
    Assembling = "Assembling"
    Released = "Released"
    Failed = "Failed"


class UploadMetadata:

    def __init__(self, name, contract, runtime, install_command, metadata, monitoring_configuration: dict):
        self.contract = contract
        self.runtime = runtime
        self.name = name
        self.installCommand = install_command
        self.metadata = metadata
        self.monitoring_configuration = monitoring_configuration


class Model:
    def __init__(self, name, runtime, contract, payload,
                 training_data_file, install_command, monitoring, metadata,
                 monitoring_configuration: MonitoringConfiguration):
        self.name = name
        self.runtime = runtime
        self.contract = contract
        self.payload = payload
        self.training_data_file = training_data_file
        self.install_command = install_command
        self.monitoring = monitoring
        self.metadata = metadata

        if not monitoring_configuration:
            monitoring_configuration = MonitoringConfiguration()
        self.monitoring_configuration = monitoring_configuration

    def validate(self):
        if not isinstance(self.name, str):
            raise InvalidModelException("name is not a string", self.__dict__)

        if self.runtime is None or not isinstance(self.runtime, DockerImage):
            raise InvalidModelException("runtime is invalid: {}".format(self.runtime), self.__dict__)

        if self.contract is not None and not isinstance(self.contract, ModelContract):
            raise InvalidModelException("contract is not a ModelContract", self.__dict__)

        if not isinstance(self.payload, list):
            raise InvalidModelException("payload is not a list", self.__dict__)

        if self.install_command is not None and not isinstance(self.install_command, str):
            raise InvalidModelException("install-command is not a string", self.__dict__)

        if self.metadata and not isinstance(self.metadata, dict):
            raise InvalidModelException("metadata is not a dictionary", self.__dict__)


class InvalidModelException(RuntimeError):
    def __init__(self, msg, model_dict):
        super().__init__(msg)
        self.model_dict = model_dict
