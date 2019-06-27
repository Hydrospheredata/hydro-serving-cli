from typing import Union, Dict, Tuple

import grpc
import hydro_serving_grpc as hs_grpc
import hydro_serving_grpc.gateway as hsg
import numpy as np
import pandas as pd
from google.protobuf.json_format import MessageToDict
from hydro_serving_grpc import manager as hsm
from google.protobuf.wrappers_pb2 import Int64Value

from hydro_serving_grpc import DT_STRING, DT_BOOL, \
    DT_HALF, DT_FLOAT, DT_DOUBLE, DT_INT8, DT_INT16, \
    DT_INT32, DT_INT64, DT_UINT8, DT_UINT16, DT_UINT32, \
    DT_UINT64, DT_COMPLEX64, DT_COMPLEX128
from google.protobuf import empty_pb2

# Useful dictionaries

NP_TO_HS_DTYPE = {
    np.int8: DT_INT8,
    np.int16: DT_INT16,
    np.int32: DT_INT32,
    np.int64: DT_INT64,
    np.uint8: DT_UINT8,
    np.uint16: DT_UINT16,
    np.uint32: DT_UINT32,
    np.uint64: DT_UINT64,
    np.float16: DT_HALF,
    np.float32: DT_FLOAT,
    np.float64: DT_DOUBLE,
    np.float128: None,
    np.complex64: DT_COMPLEX64,
    np.complex128: DT_COMPLEX128,
    np.complex256: None,
    np.bool: DT_BOOL,
    np.object: None,
    np.str: DT_STRING,
    np.void: None
}

HS_TO_NP_DTYPE = dict([(v, k) for k, v in NP_TO_HS_DTYPE.items()])

HS_DTYPE_TO_STR = {
    DT_STRING: "DT_STRING",
    DT_BOOL: "DT_BOOL",

    DT_HALF: "DT_FLOAT16",
    DT_FLOAT: "DT_FLOAT32",
    DT_DOUBLE: "DT_FLOAT64",

    DT_INT8: "DT_INT8",
    DT_INT16: "DT_INT16",
    DT_INT32: "DT_INT32",
    DT_INT64: "DT_INT64",

    DT_UINT8: "DT_UINT8",
    DT_UINT16: "DT_UINT16",
    DT_UINT32: "DT_UINT32",
    DT_UINT64: "DT_UINT64",

    DT_COMPLEX64: "DT_COMPLEX64",
    DT_COMPLEX128: "DT_COMPLEX128"
}

STR_TO_HS_DTYPE = dict([(v, k) for k, v in HS_DTYPE_TO_STR.items()])

NP_DTYPE_TO_ARG_NAME = {
    np.float16: "half_val",
    np.float32: "float_val",
    np.float64: "double_val",

    np.int8: "int_val",
    np.int16: "int_val",
    np.int32: "int_val",
    np.int64: "int64_val",
    np.uint8: "int_val",
    np.uint16: "int_val",
    np.uint32: "uint32_val",
    np.uint64: "uint64_val",
    np.float128: None,
    np.complex64: "scomplex_val",
    np.complex128: "dcomplex_val",
    np.complex256: None,
    np.bool: "bool_val",
    np.object: None,
    np.str: "string_val",
    np.void: None

}


class HydroServingClient:
    """
    HydroServingClinet is responsible for connection to grpc endpoints
    and fetches model versions
    """

    def __init__(self, grpc_url: str = '127.0.0.1:9090', secure=False):
        self.url = grpc_url
        if not secure:
            self.grpc_channel = grpc.insecure_channel(grpc_url)
        else:
            credentials = grpc.ssl_channel_credentials()
            self.grpc_channel = grpc.secure_channel(grpc_url, credentials=credentials)

        self.__manager_client = hsm.ManagerServiceStub(self.grpc_channel)
        self.prediction_client = hs_grpc.PredictionServiceStub(self.grpc_channel)
        self.gateway_client = hsg.GatewayServiceStub(self.grpc_channel)

    def get_model(self, model_name: str, model_version: int = -1):
        """
        Return an instance of HydroServingModelVersion with desired model version. -1 is the int alias
        for the last version
        :param model_name: n
        :param model_version:
        :return:
        """
        empty = empty_pb2.Empty()
        model_versions = filter(lambda x: x.model.name == model_name, self.__manager_client.GetAllVersions(empty))
        model_versions = list(model_versions)
        model_versions.sort(key=lambda x: x.version)
        model_version_serial_numbers = [mv.version for mv in model_versions]
        model_versions = dict(zip(model_version_serial_numbers, model_versions))

        if len(model_versions) == 0:
            raise ValueError("No model versions of \"{model_name}\"")
        if model_version == -1:
            return HydroServingModelVersion(model_versions[model_version_serial_numbers[-1]], self)
        elif model_version not in model_versions:
            raise ValueError(f"Invalid model_version. Got {model_version},"
                             f" but {model_name} has following versions: {model_version_serial_numbers}")
        else:
            return HydroServingModelVersion(model_versions[model_version], self)


class HSContract:
    """
    HydroServingContract contains useful info about input/output
    tensors and verifies passed dictionary for compliance with contract
    """

    def __str__(self) -> str:
        return f"Input tensors = {self.input_names}; Output tensors = {self.output_names} "

    def __init__(self, model_version_proto):
        model_proto_dict = MessageToDict(model_version_proto, preserving_proto_field_name=True)
        self.contract_dict: Dict = model_proto_dict['contract']['predict']

        outputs = self.contract_dict['outputs']
        inputs = self.contract_dict['inputs']

        hs_proto_shape_to_np_shape = lambda x: tuple([int(s['size']) for s in x['shape'].get('dim', [])])

        self.output_names = [x['name'] for x in outputs]
        self.output_shapes = dict([(x['name'], hs_proto_shape_to_np_shape(x)) for x in outputs])
        self.output_dtypes = dict([(x['name'], HS_TO_NP_DTYPE[STR_TO_HS_DTYPE[x['dtype']]]) for x in outputs])
        self.number_of_output_tensors = len(outputs)

        self.input_names = [x['name'] for x in inputs]
        self.input_shapes = dict([(x['name'], hs_proto_shape_to_np_shape(x)) for x in inputs])
        self.input_is_scalar = dict([(k, v == tuple([])) for k, v in self.input_shapes.items()])
        self.input_dtypes = dict([(x['name'], HS_TO_NP_DTYPE[STR_TO_HS_DTYPE[x['dtype']]]) for x in inputs])
        self.number_of_input_tensors = len(inputs)

    def verify_input_dict(self, x: Dict[str, np.array]) -> (bool, str):
        """
        False if x is not compliant with this contract
        """
        valid = True
        error_message = ""

        # Check for tensor names
        tensor_names = set(x.keys())
        input_names = set(self.input_names)

        if not tensor_names == input_names:
            valid = False
            tensor_names_error_message = "Invalid input tensor names.\n"
            missing_fields = input_names.difference(tensor_names)
            extra_fields = tensor_names.difference(input_names)
            if missing_fields:
                tensor_names_error_message += f"Missing tensors: {missing_fields}\n "
            if extra_fields:
                tensor_names_error_message += f"Extra tensors: {extra_fields}.\n"
            error_message += tensor_names_error_message

        # Check for tensor shapes and dtypes
        tensor_shapes_error_message = ""
        tensor_dtypes_error_message = ""
        for tensor_name in self.input_names:
            if not HSContract.shape_compliant(self.input_shapes[tensor_name], x[tensor_name].shape):
                valid = False
                tensor_shapes_error_message += f"Tensor \"{tensor_name}\" is {x[tensor_name].shape}," \
                    f" expected {self.input_shapes[tensor_name]}\n"

            if not HSContract.dtype_compliant(self.input_dtypes[tensor_name], x[tensor_name].dtype):
                valid = False
                print("1")

                tensor_dtypes_error_message += f" Tensor \"{tensor_name}\" is {x[tensor_name].shape}," \
                    f" expected {self.input_shapes[tensor_name]}"

        error_message += tensor_shapes_error_message
        error_message += tensor_shapes_error_message

        return valid, error_message

    def make_tensor_shape_proto(self, name):
        return hs_grpc.TensorShapeProto(dim=[hs_grpc.TensorShapeProto.Dim(size=x) for x in self.input_shapes[name]])

    def get_payload_arg_name(self, tensor_name):
        np_dtype = self.input_dtypes[tensor_name]
        return NP_DTYPE_TO_ARG_NAME[np_dtype]

    def make_proto(self, input_dict: Dict[str, np.array]) -> Dict[str, hs_grpc.TensorProto]:
        input_proto_dict = dict()
        for k, v in input_dict.items():
            kwargs = {self.get_payload_arg_name(k): v.flatten(),
                      "dtype": NP_TO_HS_DTYPE[self.input_dtypes[k]],
                      "tensor_shape": self.make_tensor_shape_proto(k)}
            input_proto_dict[k] = hs_grpc.TensorProto(**kwargs)

        return input_proto_dict

    @staticmethod
    def dtype_compliant(contract_dtype: np.dtype, tensor_dtype: np.dtype) -> bool:
        # Use np.can_cast rules in future?
        return tensor_dtype == contract_dtype

    @staticmethod
    def shape_compliant(contract_shape: Tuple, tensor_shape: Tuple) -> bool:
        if len(tensor_shape) == 0:
            # scalar input can be used in following scenarios
            return contract_shape == (-1, 1) or contract_shape == (1,) or contract_shape == tuple()
        if len(contract_shape) == len(tensor_shape):
            return all([s1 == -1 or s1 == s2 for s1, s2 in zip(contract_shape, tensor_shape)])
        else:
            return False


class ContractViolationException(Exception):
    """
    Exception raised after failed compliance check
    """
    pass


class HydroServingModelVersion:
    def __init__(self, model_proto, hs_client: HydroServingClient):
        self.version: int = model_proto.version
        self.name: str = model_proto.model.name
        self.__id = model_proto.id
        self.contract: HSContract = HSContract(model_proto)  # make contract
        self.__model_spec = hs_grpc.ModelSpec(name=self.name, version=Int64Value(value=self.version))
        self.__hs_client = hs_client

    def __str__(self):
        return f"{self.name}.{self.version}"

    def __repr__(self):
        return f"HydroServingModelVersion \"{self.name}\" v{self.version}"

    def __call__(self, x: Union[pd.DataFrame, pd.Series, Dict[str, np.array]] = None, _profile: bool = True, **kwargs) \
            -> Union[Dict[str, np.array]]:

        input_dict: Dict[str, np.array] = self.__make_input_dict(x, kwargs)

        is_valid_input, input_error = self.contract.verify_input_dict(input_dict)
        if not is_valid_input:
            raise ContractViolationException(str(input_error))

        input_proto: Dict[str, hs_grpc.TensorProto] = self.contract.make_proto(input_dict)

        request = hs_grpc.PredictRequest(model_spec=self.__model_spec, inputs=input_proto)

        if _profile:
            result = self.__hs_client.prediction_client.Predict(request)
        else:
            result = self.__hs_client.gateway_client.PredictModelOnly(request)

        output_dict: Dict = self.__decode_pr(result)
        return output_dict

    def __check_for_python_builtins(self, d: Dict) -> Dict:
        """
        Checks for python builtin dtypes in scalar fields of input dict
        and transforms them into suitable versions of np.dtype. If no
        safe conversion is available, raise an Exception
        :param d: input dict
        :return: output dict, without python built-in scalar dtypes
        """
        new_dict = {}
        for k, v in d.items():
            if self.contract.input_is_scalar[k]:
                if v in (0, 1):
                    # Minimum scalar dtype for 0 or 1 is `uint8`, but it
                    # cannot be casted into `bool` safely. So, we detect
                    # for bool scalars by hand.
                    min_input_dtype = np.bool
                else:
                    min_input_dtype = np.min_scalar_type(v)

                if np.can_cast(min_input_dtype, self.contract.input_dtypes[k]):
                    new_dict[k] = self.contract.input_dtypes[k](v)
                else:
                    raise ValueError(f"Can not cast {k} from {min_input_dtype} to {self.contract.input_dtypes[k]}")
            else:
                new_dict[k] = v
        return new_dict

    def __make_input_dict(self, x, kwargs) -> Dict[str, np.array]:
        """
        Transform input into input_dict which is used as core representation to check contracts. Input
        must be provided exclusively either as single argument x or by kwargs.
        :param self:
        :param x: Input which will be decoded implicitly into Dict[str, np.array]
        :type x: Union[pd.Series, Dict, pd.DataFrame, np.array]
        :param kwargs: Dictionary with tensors split according to tensor names, as specified in contract
        :type kwargs: Dict[str, np.array]
        :return:
        """
        if len(kwargs) > 0 and x is not None:
            raise ValueError("Too much arguments. Pass your data either in \'x\' or kwargs")

        if x is None and len(kwargs) is None:
            raise ValueError("No data is passed")

        if len(self.contract.input_names) == 1:
            return self.__make_input_dict_from_single_tensor(x, kwargs)

        if type(x) is dict:
            x = self.__check_for_python_builtins(x)
            input_dict = x
        elif type(x) is pd.Series:
            input_dict = dict(x)
        elif type(x) is pd.DataFrame:
            input_dict = dict(x)
            # Reshape into columnar form
            input_dict = dict([(k, np.array(v).reshape((-1, 1))) for k, v in input_dict.items()])
        elif type(x) is np.ndarray:
            raise NotImplementedError("Implicit conversion of single np.array in multi-tensor contracts is not supported")
        elif x is None:
            kwargs = self.__check_for_python_builtins(kwargs)
            input_dict = kwargs
        else:
            raise ValueError(f"Conversion failed. Expected [pandas.DataFrame, numpy.array, pandas.Series, dict], got {type(x)}")
        return input_dict

    def __make_input_dict_from_single_tensor(self, x, kwargs) -> Dict[str, np.array]:
        """
        Similar to `__make_input_dict`, but transforms input into input_dict without need of tensor name.
        Tensor name is used implicitly, since contract has only single tensor.
        :param x:
        :param kwargs:
        :return:
        """
        if len(kwargs) > 1:
            raise ValueError(f"Too much arguments. Contract has only singe tensor \'{self.contract.output_names[0]}\'")

        if len(kwargs) == 1:
            input_tensor = np.array(list(kwargs.values())[0])
        else:
            input_tensor = np.array(x)

        input_name = self.contract.input_names[0]
        contract_shape = self.contract.input_shapes[input_name]
        contract_dtype = self.contract.input_dtypes[input_name]

        if not HSContract.shape_compliant(contract_shape, input_tensor.shape):
            raise ValueError(
                f"Conversion failed at tensor \"{input_name}\". Invalid shape: {input_tensor.shape}, Expected  {contract_shape}")
        if not HSContract.dtype_compliant(contract_dtype, input_tensor.dtype):
            raise ValueError(
                f"Conversion failed at tensor \"{input_name}\". Invalid dtype: {input_tensor.dtype}, Expected {contract_dtype}")
        input_dict = {self.contract.input_names[0]: input_tensor}
        return input_dict

    def __decode_pr(self, proto: hs_grpc.tf.api.predict_pb2.PredictResponse) -> Dict[str, np.array]:
        """
        Transform PredictResponse proto into dictionary with np.arrays. We trust gateway to return us only
        valid output, so we do not check contract compliance
        """
        output_dict = {}
        for k, v in MessageToDict(proto, preserving_proto_field_name=True)['outputs'].items():
            dtype = HS_TO_NP_DTYPE[STR_TO_HS_DTYPE[v['dtype']]]
            value = proto.outputs[k].__getattribute__(NP_DTYPE_TO_ARG_NAME[dtype])
            if v['tensor_shape']:
                shape = [int(s['size']) for s in v['tensor_shape']['dim']]
                value = np.array(value, dtype=dtype).reshape(shape)
            else:
                value = np.array(value, dtype=dtype).item()

            output_dict[k] = value

        return output_dict
