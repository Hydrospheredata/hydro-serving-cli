from typing import Dict, Tuple

import hydro_serving_grpc as hs_grpc
import numpy as np
import pandas as pd
import yaml
from hydro_serving_grpc.contract import ModelContract

from .proto_conversions import NP_TO_HS_DTYPE, NP_DTYPE_TO_ARG_NAME, proto2np_dtype, np2proto_dtype, proto2np_shape, np2proto_shape
from ..core.contract import DTYPE_TO_NAMES as HS_DTYPE_TO_NAME, NAME_TO_DTYPES as NAME_TO_HS_DTYPE


class AlwaysTrueObj(object):
    def __eq__(self, other):
        return True


AnyDimSize = AlwaysTrueObj()

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


class ContractViolationException(Exception):
    """
    Exception raised after failed compliance check
    """
    pass


class HSContract:
    """
    Python wrapper around proto object of ModelContract.
    HydroServingContract contains useful info about input/output
    tensors and verifies passed dictionary for compliance with contract.
    """

    def __init__(self, model_name, signature_name, inputs, outputs):

        self.model_name = model_name

        self.signature_name = signature_name

        self.output_names = [t['name'] for t in outputs]
        self.output_shapes = dict([(t['name'], t['shape']) for t in outputs])
        self.output_dtypes = dict([(t['name'], t['dtype']) for t in outputs])
        self.output_profiles = dict([(t['name'], t['profile']) for t in outputs])

        self.input_names = [t['name'] for t in inputs]
        self.input_shapes = dict([(t['name'], t['shape']) for t in inputs])
        self.input_dtypes = dict([(t['name'], t['dtype']) for t in inputs])
        self.input_profiles = dict([(t['name'], t['profile']) for t in inputs])

    def __str__(self) -> str:
        return "Input tensors = {}; Output tensors = {}".format(self.input_names, self.output_names)

    @property
    def proto(self):
        tensor_inputs = []
        for input_tensor_name in self.input_names:
            _dtype = np2proto_dtype(self.input_dtypes[input_tensor_name])
            _shape = np2proto_shape(self.input_shapes[input_tensor_name])
            _profile = self.input_profiles[input_tensor_name]

            tensor = hs_grpc.contract.ModelField(name=input_tensor_name, shape=_shape, dtype=_dtype)
            tensor_inputs.append(tensor)

        tensor_outputs = []
        for output_tensor_name in self.output_names:
            _dtype = np2proto_dtype(self.output_dtypes[output_tensor_name])
            _shape = np2proto_shape(self.output_shapes[output_tensor_name])
            _profile = self.output_profiles[output_tensor_name]
            tensor = hs_grpc.contract.ModelField(name=output_tensor_name, shape=_shape, dtype=_dtype)
            tensor_outputs.append(tensor)

        signature = hs_grpc.contract.ModelSignature(signature_name=self.signature_name,
                                                    inputs=tensor_inputs, outputs=tensor_outputs)
        contract_proto = ModelContract(model_name=self.model_name, predict=signature)
        return contract_proto

    @classmethod
    def from_proto(cls, contract_proto: ModelContract):
        inputs = []
        for input_tensor in contract_proto.predict.inputs:
            inputs.append({"name": input_tensor.name,
                           "shape": proto2np_shape(input_tensor.shape),
                           "dtype": proto2np_dtype(input_tensor.dtype),
                           "profile": input_tensor.profile})

        outputs = []
        for output_tensor in contract_proto.predict.outputs:
            outputs.append({"name": output_tensor.name,
                            "shape": proto2np_shape(output_tensor.shape),
                            "dtype": proto2np_dtype(output_tensor.dtype),
                            "profile": output_tensor.profile})

        return cls(contract_proto.model_name, contract_proto.predict.signature_name, inputs, outputs)

    @classmethod
    def from_df(cls, input_df: pd.DataFrame):
        """
        Suggest contract definition for model contract from dataframe
        :param input_df:
        :return:
        """

        model_name = getattr(input_df, "name", "random_model_name")
        signature_name = "predict"

        inputs = []
        for name, dtype in zip(input_df.columns, input_df.dtypes):
            inputs.append({"name": name,
                           "dtype": dtype.type,
                           "shape": (-1, 1),
                           "profile": None})

        outputs = []

        return cls(model_name, signature_name, inputs, outputs)

    @classmethod
    def load(cls, fp):
        """
        Load contract from YAML file
        :param fp:
        :return:
        """
        yaml_contract = yaml.load(fp, Loader)
        inputs = []
        for input_tensor_name, props in yaml_contract['contract']['inputs'].items():

            if props['type'] in NAME_TO_HS_DTYPE:
                dtype = proto2np_dtype(NAME_TO_HS_DTYPE[props['type']])
            else:
                dtype = proto2np_dtype(hs_grpc.DataType.Value(props['type']))

            profile = props.get('profile', "NONE")

            if props['shape'] == "scalar":
                shape = tuple()
            else:
                shape = tuple(props['shape'])

            inputs.append({"shape": shape, "dtype": dtype, "profile": profile, "name": input_tensor_name})

        outputs = []
        for output_tensor_name, props in yaml_contract['contract']['outputs'].items():

            if props['type'] in NAME_TO_HS_DTYPE:
                dtype = proto2np_dtype(NAME_TO_HS_DTYPE[props['type']])
            else:
                dtype = proto2np_dtype(hs_grpc.DataType.Value(props['type']))

            profile = props.get('profile', "NONE")

            if props['shape'] == "scalar":
                shape = tuple()
            else:
                shape = tuple(props['shape'])

            outputs.append({"shape": shape, "dtype": dtype, "profile": profile, "name": output_tensor_name})

        return cls(yaml_contract['name'], yaml_contract['contract'].get('name', "predict"), inputs, outputs)

    def dump(self, fp):
        """
        Dump current contract into YAML file
        """

        yaml_contract = {"kind": "Model",
                         "payload": ["src/", "requirements.txt"],
                         "runtime": "hydrosphere/serving-runtime-python-3.6:0.1.2-rc0",
                         "install-command": "pip install -r requirements.txt"}
        inputs = {}

        for input_tensor_name in self.input_names:
            dtype = HS_DTYPE_TO_NAME[NP_TO_HS_DTYPE[self.input_dtypes[input_tensor_name]]]
            profile = self.input_profiles[input_tensor_name]
            shape = list(self.input_shapes[input_tensor_name])
            if not shape:
                shape = "scalar"
            inputs[input_tensor_name] = {"shape": shape, "type": dtype}
            if not profile:
                inputs[input_tensor_name]["profile"] = profile

        outputs = {}
        for output_tensor_name in self.output_names:
            dtype = HS_DTYPE_TO_NAME[NP_TO_HS_DTYPE[self.output_dtypes[output_tensor_name]]]
            profile = self.output_profiles[output_tensor_name]
            shape = list(self.output_shapes[output_tensor_name])
            if not shape:
                shape = 'scalar'
            outputs[output_tensor_name] = {"shape": shape, "type": dtype}
            if not profile:
                outputs[output_tensor_name]["profile"] = profile

        yaml_contract['contract'] = {}
        yaml_contract['name'] = self.model_name
        yaml_contract['contract']['name'] = self.signature_name
        yaml_contract['contract']['inputs'] = inputs
        yaml_contract['contract']['outputs'] = outputs

        yaml.dump(yaml_contract, fp, allow_unicode=True, default_flow_style=None)

    # Request-Response Conversions

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
                tensor_names_error_message += "Missing tensors: {}\n ".format(missing_fields)
            if extra_fields:
                tensor_names_error_message += "Extra tensors: {}.\n".format(extra_fields)
            error_message += tensor_names_error_message

        # Check for tensor shapes and dtypes
        tensor_shapes_error_message = ""
        tensor_dtypes_error_message = ""
        for tensor_name in self.input_names:
            if not HSContract.shape_compliant(self.input_shapes[tensor_name], x[tensor_name].shape):
                valid = False
                tensor_shapes_error_message += "Tensor \"{}\" is {},expected {}".format(tensor_name, x[tensor_name].shape,
                                                                                        self.input_shapes[tensor_name])

            if not HSContract.dtype_compliant(self.input_dtypes[tensor_name], x[tensor_name].dtype):
                valid = False
                tensor_dtypes_error_message += "Tensor \"{}\" is {},expected {}".format(tensor_name, x[tensor_name].dtype,
                                                                                        self.input_dtypes[tensor_name])

        error_message += tensor_shapes_error_message
        error_message += tensor_dtypes_error_message

        return valid, error_message

    def get_payload_arg_name(self, tensor_name):
        """
        Get name under which we store data in tensor proto
        dependent on dtype
        :param tensor_name:
        :return:
        """
        return NP_DTYPE_TO_ARG_NAME[self.input_dtypes[tensor_name]]

    def make_proto(self, input_dict: Dict[str, np.array]) -> Dict[str, hs_grpc.TensorProto]:
        """
        Transforms Dict with ndarray tensors into dict with TensorProtos, according to
        contract
        :param input_dict:
        :return:
        """
        input_proto_dict = dict()
        for tensor_name, tensor_values in input_dict.items():
            kwargs = {self.get_payload_arg_name(tensor_name): tensor_values.flatten(),
                      "dtype": NP_TO_HS_DTYPE[self.input_dtypes[tensor_name]],
                      "tensor_shape": np2proto_shape(self.input_shapes[tensor_name])}
            input_proto_dict[tensor_name] = hs_grpc.TensorProto(**kwargs)

        return input_proto_dict

    @staticmethod
    def dtype_compliant(contract_dtype: np.dtype, tensor_dtype: np.dtype) -> bool:
        # Use np.can_cast rules in future?
        return tensor_dtype == contract_dtype

    @staticmethod
    def shape_compliant(contract_shape: Tuple, tensor_shape: Tuple) -> bool:
        if len(contract_shape) == 0:
            # scalar input can be used in following scenarios
            if tensor_shape == tuple():
                return True
            else:
                return max(tensor_shape) == 1  # All dimensions are equal to 1

        if len(contract_shape) == len(tensor_shape):
            possible_contract_shape = tuple([AnyDimSize if s == -1 else s for s in contract_shape])
            return possible_contract_shape == tensor_shape
        else:
            return False

    @staticmethod
    def decode_list_of_tensors(fields):
        """
        Transform imput fields dict into dictionary with np.arrays. We trust gateway to return us only
        valid input, so we do not check contract compliance
        """
        d = {}
        for tensor_name, field in fields.items():
            dtype = proto2np_dtype(field.dtype)
            value = field.__getattribute__(NP_DTYPE_TO_ARG_NAME[dtype])
            shape = proto2np_shape(field.tensor_shape)

            if shape != tuple():
                value = np.array(value, dtype=dtype).reshape(shape)
            else:
                value = np.array(value, dtype=dtype).item()

            d[tensor_name] = value

        return d

    def __check_for_python_scalars(self, d: Dict) -> Dict:
        """
        Checks for python builtin dtypes in scalar fields of input dict
        and transforms them into suitable versions of np.dtype. If no
        safe conversion is available, raise an Exception
        :param d: input dict
        :return: output dict, without python built-in scalar dtypes
        """
        new_dict = {}
        for name, val in d.items():
            if self.input_shapes[name] == tuple():
                if val in (0, 1):
                    # Minimum scalar dtype for 0 or 1 is `uint8`, but it
                    # cannot be casted into `bool` safely. So, we detect
                    # for bool scalars by hand.
                    min_input_dtype = np.bool
                else:
                    min_input_dtype = np.min_scalar_type(val)

                if np.can_cast(min_input_dtype, self.input_dtypes[name]):
                    new_dict[name] = self.input_dtypes[name](val)
                else:
                    raise ValueError("Can not cast {} from {} to {}".format(name, min_input_dtype, self.input_dtypes[name]))
            else:
                new_dict[name] = val
        return new_dict

    def make_input_dict(self, x, kwargs) -> Dict[str, np.array]:
        """
        Transform input into input_dict which is used as core representation to check contracts. Input
        must be provided exclusively either as single argument x or by kwargs.
        :param self:
        :param x: Input which will be decoded implicitly into Dict[str, np.array]
        :type x: Union[Dict, pd.DataFrame, np.array]
        :type x: Union[Dict, pd.DataFrame, np.array]
        :param kwargs: Dictionary with tensors split according to tensor names, as specified in contract
        :type kwargs: Dict[str, np.array]
        :return:
        """
        if len(kwargs) > 0 and x is not None:
            raise ValueError("Too much arguments. Pass your data either in \'x\' or kwargs")

        if x is None and len(kwargs) is None:
            raise ValueError("No data is passed")

        if len(self.input_names) == 1:
            return self.make_input_dict_from_single_tensor(x, kwargs)

        if type(x) is dict:
            x = self.__check_for_python_scalars(x)
            input_dict = x
        elif type(x) is pd.DataFrame:
            input_dict = dict(x)
            # Reshape into columnar form
            input_dict = dict([(k, np.array(v).reshape((-1, 1))) for k, v in input_dict.items()])
        elif type(x) is np.ndarray:
            raise NotImplementedError("Implicit conversion of single np.array in multi-tensor contracts is not supported")
        elif x is None:
            kwargs = self.__check_for_python_scalars(kwargs)
            input_dict = kwargs
        else:
            raise ValueError("Conversion failed. Expected [pandas.DataFrame, numpy.array, dict], got {}".format(type(x)))
        return input_dict

    def make_input_dict_from_single_tensor(self, x, kwargs) -> Dict[str, np.array]:
        """
        Similar to `make_input_dict`, but transforms input into input_dict without need of tensor name.
        Tensor name is used implicitly, since contract has only single tensor.
        Tensor name is used implicitly, since contract has only single tensor.
        :param x:
        :param kwargs:
        :return:
        """
        if len(kwargs) > 1:
            raise ValueError("Too much arguments. Contract has only singe tensor \'{}\'".format(self.output_names[0]))

        input_name = self.input_names[0]
        if len(kwargs) == 1:
            input_tensor = list(kwargs.values())[0]
        else:
            input_tensor = x

        input_dict = {input_name: np.array(input_tensor)}
        return input_dict
