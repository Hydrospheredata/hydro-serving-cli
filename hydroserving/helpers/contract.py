import os
import logging
from numbers import Number

from hydro_serving_grpc import ModelContract, TensorShapeProto
from google.protobuf import text_format
from hydroserving.models.definitions.model import Model

log = logging.getLogger('helpers.contract')

def model_to_contract(model):
    if not isinstance(model, Model):
        raise TypeError("{} is not a Model".format(type(model)))
    log.debug(model)
    None


def read_contract_cwd(model):
    if model.contract_path is not None:
        return read_contract_file(model.contract_path)
    return None


def read_contract_file(contract_path):
    _, file_ext = os.path.splitext(contract_path)
    contract = ModelContract()

    if file_ext == ".protobin" or file_ext == ".pb":
        with open(contract_path, "rb") as contract_file:
            contract.ParseFromString(contract_file.read())
    elif file_ext:
        with open(contract_path, "r") as contract_file:
            text_format.Parse(contract_file.read(), contract)
    else:
        raise RuntimeError("Unsupported contract extension")
    return contract


def shape_to_proto(shape_list):
    if shape_list is None:
        return None
    if not isinstance(shape_list, list):
        raise TypeError("shape_list is not a list", shape_list)

    dims = []
    for dim in shape_list:
        if not isinstance(dim, Number):
            raise TypeError("shape_list contains incorrect dim", shape_list, dim)
        converted = TensorShapeProto.Dim(size=dim)
        dims.append(converted)
    shape = TensorShapeProto(dim=dims)
    return shape
