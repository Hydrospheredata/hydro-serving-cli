import logging
from enum import Enum
from typing import Union, Dict

import grpc
import hydro_serving_grpc as hs_grpc
import hydro_serving_grpc.gateway as hsg
import pandas as pd
import requests
from google.protobuf import empty_pb2

from .contract import HSContract, ContractViolationException
from .proto_conversions import *


class HSApplication:
    """
    HydroServingApplication. Collection of models
    """

    def __init__(self, hs_client, application_name):
        resp = requests.get("https://{}/api/v2/application/{}".format(hs_client.url, application_name))
        if resp.ok:
            app_json = resp.json()
        else:
            raise Exception(resp.text)

        def process_model_variant(d: Dict):
            return {'model': hs_client.get_model(d['modelVersion']['model']['name'], d['modelVersion']['modelVersion']),
                    'weight': d['weight']}

        self.name = application_name
        self.executionGraph = [[process_model_variant(m) for m in s['modelVariants']] for s in app_json['executionGraph']['stages']]
        self.spec = hs_grpc.ModelSpec(name=application_name)

        self.contract = HSContract("name", "predict", app_json['signature'])

        self.__hs_client = hs_client

    def __call__(self, x: Union[pd.DataFrame, pd.Series, Dict[str, np.array], None] = None,
                 _profile: bool = False, **kwargs):
        input_dict = self.contract.make_input_dict(x, kwargs)
        is_valid_input, input_error = self.contract.verify_input_dict(input_dict)

        if not is_valid_input:
            raise ContractViolationException(str(input_error))

        input_proto = self.contract.make_proto(input_dict)

        request = hs_grpc.PredictRequest(model_spec=self.spec, inputs=input_proto)
        result = self.__hs_client._HydroServingClient__prediction_stub.Predict(request)
        output_dict = self.contract.decode_list_of_tensors(result.outputs)
        return output_dict

    def __repr__(self):
        return "Application \"{}\";\n Models: {}".format(self.name, [[str(m['model']) for m in stage] for stage in self.executionGraph])


class HSServable:
    """
    Servable used for making inference calls
    """

    def __init__(self, servable_name, model_proto, hs_client):
        self.version = model_proto.version
        self.servable_name = servable_name
        self.model_name = model_proto.model.name
        self.id = model_proto.id
        self.contract = HSContract.from_proto(model_proto.contract)
        self.__hs_client = hs_client

    def __repr__(self):
        return "{} v{}, servable_id = {}".format(self.model_name, self.version, self.servable_name)

    def __call__(self,
                 x: Union[pd.DataFrame, pd.Series, Dict[str, np.array], None] = None,
                 _profile: bool = False, **kwargs) \
            -> Union[Dict[str, np.array]]:

        input_dict = self.contract.make_input_dict(x, kwargs)
        is_valid_input, input_error = self.contract.verify_input_dict(input_dict)

        if not is_valid_input:
            raise ContractViolationException(str(input_error))

        input_proto = self.contract.make_proto(input_dict)

        request = hs_grpc.gateway.ServablePredictRequest(servable_name=self.servable_name, data=input_proto)

        if _profile:
            result = self.__hs_client._HydroServingClient__gateway_stub.PredictServable(request)
        else:
            result = self.__hs_client._HydroServingClient__gateway_stub.ShadowlessPredictServable(request)

        output_dict = self.contract.decode_list_of_tensors(result.outputs)
        return output_dict

    def remove(self, ):
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

    def __init__(self, model_proto, hs_client):
        self.version = model_proto.version
        self.model_name = model_proto.model.name
        self.id = model_proto.id
        self.contract = HSContract.from_proto(model_proto.contract)  # make contract
        self.__hs_client = hs_client

    def __repr__(self):
        return "Model \"{}\" v{}".format(self.model_name, self.version)

    def __call__(self, *args, **kwargs):
        raise NotImplementedError("Prediction through HydroServingModel is not possible. Use HydroServingServable instead")

    def create_servable(self) -> HSServable:
        """
        Alias for 'HydroServingClient.create_servable' method
        :return: new servable of this model
        """
        return self.__hs_client.create_servable(self.model_name, self.version)


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

        self.__manager_stub = hs_grpc.manager.ManagerServiceStub(self.grpc_channel)
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
            raise ValueError("No model versions of \"{}\"".format(model_name))
        if model_version == -1:
            return HSModel(model_versions[model_version_serial_numbers[-1]], self)
        elif model_version not in model_versions:
            raise ValueError("Invalid model_version. Got {}, but {} has following versions: {}".format(model_version, model_name,
                                                                                                       model_version_serial_numbers))
        else:
            return HSModel(model_versions[model_version], self)

    def get_application(self, application_name: str) -> HSApplication:
        return HSApplication(self, application_name)

    def create_servable(self, model_name: str, model_version: int = 1) -> HSServable:
        """
        Instantiate servable from model version
        :param model_name:
        :param model_version:
        :return: HydroServingServable
        """
        model_version_id = hs_grpc.manager.ModelVersionIdentifier(name=model_name, version=model_version)
        deploy_request = hs_grpc.manager.DeployServableRequest(fullname=model_version_id)

        s = None
        for s in self.__manager_stub.DeployServable(deploy_request):
            logging.info("{} is {}".format(s.name, ServableStatus(s.status)))

        if s is None:
            raise Exception("Failed to create new servable")
        else:
            return HSServable(s.name, s.model_version, self)

    def remove_servable(self, servable_name):
        remove_request = hs_grpc.manager.RemoveServableRequest(servable_name=servable_name)
        _ = self.__manager_stub.RemoveServable(remove_request)


class ServableStatus(Enum):
    NOT_SERVING = 0
    NOT_AVAILABLE = 1
    STARTING = 2
    SERVING = 3
