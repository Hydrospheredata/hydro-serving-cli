import os
import logging
from numbers import Number

from hydro_serving_grpc import ModelContract, TensorShapeProto, ModelField, ModelSignature
from google.protobuf import text_format
from hydro_serving_grpc import DT_INVALID, DT_STRING, DT_BOOL, \
    DT_HALF, DT_FLOAT, DT_DOUBLE, DT_INT8, DT_INT16, \
    DT_INT32, DT_INT64, DT_UINT8, DT_UINT16, DT_UINT32, \
    DT_UINT64, DT_QINT8, DT_QINT16, DT_QINT32, DT_QUINT8, DT_QUINT16, DT_VARIANT

log = logging.getLogger('helpers.contract')

NAME_TO_DTYPES = {
    "invalid": DT_INVALID,
    "string": DT_STRING,
    "bool": DT_BOOL,
    "variant": DT_VARIANT,

    "float16": DT_HALF,
    "half": DT_HALF,
    "float32": DT_FLOAT,
    "float64": DT_DOUBLE,
    "double": DT_DOUBLE,

    "int8": DT_INT8,
    "int16": DT_INT16,
    "int32": DT_INT32,
    "int64": DT_INT64,

    "uint8": DT_UINT8,
    "uint16": DT_UINT16,
    "uint32": DT_UINT32,
    "uint64": DT_UINT64,

    "qint8": DT_QINT8,
    "qint16": DT_QINT16,
    "qint32": DT_QINT32,

    "quint8": DT_QUINT8,
    "quint16": DT_QUINT16
}

DTYPE_TO_NAMES = {
    DT_INVALID: "invalid",
    DT_STRING: "string",
    DT_BOOL: "bool",
    DT_VARIANT: "variant",

    DT_HALF: "float16",
    DT_FLOAT: "float32",
    DT_DOUBLE: "float64",

    DT_INT8: "int8",
    DT_INT16: "int16",
    DT_INT32: "int32",
    DT_INT64: "int64",

    DT_UINT8: "uint8",
    DT_UINT16: "uint16",
    DT_UINT32: "uint32",
    DT_UINT64: "uint64",

    DT_QINT8: "qint8",
    DT_QINT16: "qint16",
    DT_QINT32: "qint32",

    DT_QUINT8: "quint8",
    DT_QUINT16: "quint16"
}


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


def shape_to_proto(user_shape):
    if user_shape == "scalar":
        shape = TensorShapeProto()
    elif user_shape is None:
        shape = None
    elif isinstance(user_shape, list):
        dims = []
        for dim in user_shape:
            if not isinstance(dim, Number):
                raise TypeError("shape_list contains incorrect dim", user_shape, dim)
            converted = TensorShapeProto.Dim(size=dim)
            dims.append(converted)
        shape = TensorShapeProto(dim=dims)
    else:
        raise ValueError("Invalid shape value", user_shape)
    return shape


def contract_from_dict(data_dict):
    if data_dict is None:
        return None
    signatures = []
    for sig_name, value in data_dict.items():
        inputs = []
        outputs = []
        for in_key, in_value in value["inputs"].items():
            input = field_from_dict(in_key, in_value)
            inputs.append(input)
        for out_key, out_value in value["outputs"].items():
            output = field_from_dict(out_key, out_value)
            outputs.append(output)
        cur_sig = ModelSignature(
            signature_name=sig_name,
            inputs=inputs,
            outputs=outputs
        )
        signatures.append(cur_sig)
    contract = ModelContract(
        signatures=signatures
    )
    return contract


def field_from_dict(name, data_dict):
    shape = data_dict.get("shape")
    dtype = data_dict.get("type")
    subfields = data_dict.get("fields")

    result_dtype = None
    result_subfields = None
    if dtype is None:
        if subfields is None:
            result_dtype = DT_INVALID
        else:
            subfields_buffer = []
            for k, v in subfields.items():
                subfield = field_from_dict(k, v)
                subfields_buffer.append(subfield)
            result_subfields = subfields_buffer
    else:
        result_dtype = NAME_TO_DTYPES.get(dtype, DT_INVALID)

    if result_dtype is not None:
        result_field = ModelField(
            name=name,
            shape=shape_to_proto(shape),
            dtype=result_dtype
        )
    elif result_subfields is not None:
        result_field = ModelField(
            name=name,
            shape=shape_to_proto(shape),
            subfields=ModelField.Subfield(data=result_subfields)
        )
    else:
        raise ValueError("Invalid field. Neither dtype nor subfields are present in dict", name, data_dict)

    return result_field
