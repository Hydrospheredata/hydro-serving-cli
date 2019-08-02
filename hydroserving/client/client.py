from enum import Enum
from typing import Union, Dict, List

import grpc
import hydro_serving_grpc as hs_grpc
import hydro_serving_grpc.gateway as hsg
import pandas as pd
from google.protobuf import empty_pb2
from hydro_serving_grpc import manager as hsm
from loguru import logger

from .contract import HSContract, ContractViolationException
from .type_conversions import *
import numpy as np


class HSApplication:
    """
    HydroServingApplication. Collection of models
    """

    def __init__(self):
        self.models: List[HSModel] = []
        pass


class HSServable:
    """
    Servable used for making inference calls
    """

    def __init__(self, servable_name, model_proto, hs_client: "HydroServingClient"):
        self.version: int = model_proto.version
        self.servable_name = servable_name
        self.model_name: str = model_proto.model.name
        self.id = model_proto.id
        self.contract: HSContract = HSContract.from_proto(model_proto)  # make contract
        self.__hs_client = hs_client

    def __str__(self):
        return f"{self.model_name} v{self.version}, servable_id = {self.servable_name}"

    def __repr__(self):
        return self.__str__()

    def __call__(self,
                 x: Union[pd.DataFrame, pd.Series, Dict[str, np.array]] = None,
                 _profile: bool = False, **kwargs) \
            -> Union[Dict[str, np.array]]:

        input_dict: Dict[str, np.array] = self.contract.make_input_dict(x, kwargs)
        is_valid_input, input_error = self.contract.verify_input_dict(input_dict)

        if not is_valid_input:
            raise ContractViolationException(str(input_error))

        input_proto: Dict[str, hs_grpc.TensorProto] = self.contract.make_proto(input_dict)

        request = hs_grpc.gateway.ServablePredictRequest(servable_name=self.servable_name, data=input_proto)

        if _profile:
            result = self.__hs_client._HydroServingClient__gateway_stub.PredictServable(request)
        else:
            result = self.__hs_client._HydroServingClient__gateway_stub.ShadowlessPredictServable(request)

        output_dict: Dict = self.contract.decode_response(result)
        return output_dict

    def delete(self, ):
        """
        Kill this servable
        :return:
        """
        return self.__hs_client.remove_servable(self.servable_name)


class HSModel:
    """
    Instance of model, instantiated from ModelVersion returned by Manager. Used only for fetching contract, model_id.
    Not used for predicting things. It can be viewed as an AbstractClass
    """

    def __init__(self, model_proto, hs_client: HydroServingClient):
        self.version: int = model_proto.version
        self.model_name: str = model_proto.model.name
        self.id = model_proto.id
        self.contract: HSContract = HSContract.from_proto(model_proto)  # make contract
        self.__hs_client = hs_client

    def __str__(self):
        return f"Model {self.model_name} v{self.version}"

    def __repr__(self):
        return f"Model \"{self.model_name}\" v{self.version}"

    def __call__(self, *args, **kwargs):
        raise NotImplementedError("Prediction through HydroServingModel is not possible. Use HydroServingServable instead")

    def make_new_servable(self) -> HSServable:
        """
        Alias for HydroServingClient deploy_servable method
        :return: new servable of this model
        """
        return self.__hs_client.deploy_servable(self.model_name, self.version)


class HydroServingClient:
    """
    HydroServingClient is responsible for connection to grpc endpoints, fetching model versions,
    deploying and removing servables.
    """

    def __init__(self, grpc_url: str, credentials=None):
        self.url = grpc_url
        if not credentials:
            self.grpc_channel = grpc.insecure_channel(grpc_url)
        else:
            self.grpc_channel = grpc.secure_channel(grpc_url, credentials=credentials)

        self.__manager_stub = hsm.ManagerServiceStub(self.grpc_channel)
        self.__prediction_stub = hs_grpc.PredictionServiceStub(self.grpc_channel)
        self.__gateway_stub = hsg.GatewayServiceStub(self.grpc_channel)

    def get_model(self, model_name: str, model_version: int = -1):
        """
        Return an instance of HydroServingModelVersion with desired model version. -1 is the int alias
        for the last version
        :param model_name:
        :param model_version:
        :return:
        """
        empty = empty_pb2.Empty()
        model_versions = filter(lambda x: x.model.name == model_name, self.__manager_stub.GetAllVersions(empty))
        model_versions = list(model_versions)
        model_versions.sort(key=lambda x: x.version)
        model_version_serial_numbers = [mv.version for mv in model_versions]
        model_versions = dict(zip(model_version_serial_numbers, model_versions))

        if len(model_versions) == 0:
            raise ValueError(f"No model versions of \"{model_name}\"")
        if model_version == -1:
            return HSModel(model_versions[model_version_serial_numbers[-1]], self)
        elif model_version not in model_versions:
            raise ValueError(f"Invalid model_version. Got {model_version},"
                             f" but {model_name} has following versions: {model_version_serial_numbers}")
        else:
            return HSModel(model_versions[model_version], self)

    def get_servable(self, servable_name: str) -> HSServable:
        raise NotImplementedError("Need to get ")

    def get_application(self, application_name: str) -> HSApplication:
        raise NotImplementedError("Applications are not supported yet!")

    def deploy_servable(self, model_name: str, model_version: int = 1) -> HSServable:
        """
        Instantiate servable from model version
        :param model_name:
        :param model_version:
        :return: HydroServingServable
        """
        model_version_id = hs_grpc.manager.ModelVersionIdentifier(name=model_name, version=model_version)
        deploy_request = hs_grpc.manager.DeployServableRequest(fullname=model_version_id)

        for s in self.__manager_stub.DeployServable(deploy_request):
            servable_status = s.status
            logger.info(f"{s.name} is {ServableStatus(servable_status)}")

        return HSServable(s.name, s.model_version, self)

    def remove_servable(self, servable_name):
        remove_request = hs_grpc.manager.RemoveServableRequest(servable_name=servable_name)
        _ = self.__manager_stub.RemoveServable(remove_request)


class ServableStatus(Enum):
    NOT_SERVING = 0
    NOT_AVAILABLE = 1
    STARTING = 2
    SERVING = 3
