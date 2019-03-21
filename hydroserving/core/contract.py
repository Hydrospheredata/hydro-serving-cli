import os
import logging
from numbers import Number

from google.protobuf import text_format
from hydro_serving_grpc import ModelContract, TensorShapeProto, ModelField, ModelSignature, \
    DT_INVALID, DT_STRING, DT_BOOL, \
    DT_HALF, DT_FLOAT, DT_DOUBLE, DT_INT8, DT_INT16, \
    DT_INT32, DT_INT64, DT_UINT8, DT_UINT16, DT_UINT32, \
    DT_UINT64, DT_QINT8, DT_QINT16, DT_QINT32, DT_QUINT8, \
    DT_QUINT16, DT_VARIANT, DataType, DT_COMPLEX64, DT_COMPLEX128, \
    DataProfileType


def contract_to_dict(contract):
    if contract is None:
        return None
    if not isinstance(contract, ModelContract):
        raise TypeError("contract is not ModelContract")
    signature = signature_to_dict(contract.predict)
    result_dict = {
        "modelName": contract.model_name,
        "predict": signature
    }
    return result_dict


def signature_to_dict(signature):
    if not isinstance(signature, ModelSignature):
        raise TypeError("signature is not ModelSignature")
    inputs = []
    for i in signature.inputs:
        inputs.append(field_to_dict(i))
    outputs = []
    for o in signature.outputs:
        outputs.append(field_to_dict(o))
    result_dict = {
        "signatureName": signature.signature_name,
        "inputs": inputs,
        "outputs": outputs
    }
    return result_dict


def field_to_dict(field):
    if not isinstance(field, ModelField):
        raise TypeError("field is not ModelField")
    result_dict = {
        "name": field.name,
        "profile": DataProfileType.Name(field.profile)
    }
    if field.shape is not None:
        result_dict["shape"] = shape_to_dict(field.shape)

    attach_ds(result_dict, field)
    return result_dict


def shape_to_dict(shape):
    dims = []
    for d in shape.dim:
        dims.append({"size": d.size, "name": d.name})
    result_dict = {
        "dim": dims,
        "unknownRank": shape.unknown_rank
    }
    return result_dict


def attach_ds(result_dict, field):
    if field.dtype is not None:
        result_dict["dtype"] = DataType.Name(field.dtype)
    elif field.subfields is not None:
        subfields = []
        for f in field.subfields:
            subfields.append(field_to_dict(f))
        result_dict["subfields"] = subfields
    else:
        raise ValueError("Invalid ModelField type")
    return result_dict


NAME_TO_DTYPES = {
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
    "quint16": DT_QUINT16,

    "complex64": DT_COMPLEX64,
    "complex128": DT_COMPLEX128,
}

DTYPE_TO_NAMES = {
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
    DT_QUINT16: "quint16",

    DT_COMPLEX64: "complex64",
    DT_COMPLEX128: "complex128"
}


def read_contract_cwd(model):
    if model.contract_path is not None:
        return read_contract_file(model.contract_path)
    return None


def read_contract_file(contract_path):
    _, file_ext = os.path.splitext(contract_path)
    contract = ModelContract()

    if file_ext in (".protobin", ".pb"):
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
    name = data_dict.get("name", "Predict")
    inputs = []
    outputs = []
    for in_key, in_value in data_dict["inputs"].items():
        input = field_from_dict(in_key, in_value)
        inputs.append(input)
    for out_key, out_value in data_dict["outputs"].items():
        output = field_from_dict(out_key, out_value)
        outputs.append(output)
    signature = ModelSignature(
        signature_name=name,
        inputs=inputs,
        outputs=outputs
    )
    contract = ModelContract(
        model_name="model",
        predict=signature
    )
    return contract


def field_from_dict(name, data_dict):
    shape = data_dict.get("shape")
    dtype = data_dict.get("type")
    subfields = data_dict.get("fields")
    raw_profile = data_dict.get("profile", "NONE")
    profile = raw_profile.upper()

    if profile not in DataProfileType.keys():
        logging.warning("Unknown data profile '%s' for field '%s'. Using 'NONE' instead.", raw_profile, name)
        profile = "NONE"

    result_dtype = None
    result_subfields = None
    if dtype is None:
        if subfields is None:
            raise ValueError("Invalid field. Neither dtype nor subfields are present in dict", name, data_dict)
        else:
            subfields_buffer = []
            for k, v in subfields.items():
                subfield = field_from_dict(k, v)
                subfields_buffer.append(subfield)
            result_subfields = subfields_buffer
    else:
        result_dtype = NAME_TO_DTYPES.get(dtype, DT_INVALID)
        if result_dtype == DT_INVALID:
            raise ValueError("Invalid contract: {} field has invalid datatype {}".format(name, dtype))

    if result_dtype is not None:
        result_field = ModelField(
            name=name,
            shape=shape_to_proto(shape),
            dtype=result_dtype,
            profile=profile
        )
    elif result_subfields is not None:
        result_field = ModelField(
            name=name,
            shape=shape_to_proto(shape),
            subfields=ModelField.Subfield(data=result_subfields),
            profile=profile
        )
    else:
        raise ValueError("Invalid field. Neither dtype nor subfields are present in dict", name, data_dict)

    return result_field
