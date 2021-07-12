from hs.entities.base_entity import BaseEntity
from typing import Dict, List, Optional, Union
from hydrosdk.signature import ModelSignature, ModelField
from hydro_serving_grpc.serving.contract.tensor_pb2 import TensorShape
from hydro_serving_grpc.serving.contract.types_pb2 import *

class Field(BaseEntity):
    shape: Union[List[int], str]
    type: str
    profile: str

class Contract(BaseEntity):
    name: Optional[str] = "predict"
    inputs: Dict[str, Field]
    outputs: Dict[str, Field]

    def to_proto(self):
        return ModelSignature(
            signature_name = self.name,
            inputs = [_convert_field(k, v) for k, v in self.inputs.items()],
            outputs = [_convert_field(k, v) for k, v in self.outputs.items()],
        )

def convert_shape(shape):
    return TensorShape(dims=shape) if isinstance(shape, list) else TensorShape()

NAME_TO_DTYPES = {
    "string": DT_STRING,
    "bool": DT_BOOL,

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

def convert_dtype(type):
    return NAME_TO_DTYPES.get(type)

def convert_profile(profile):
    return profile.upper()

def _convert_field(name: str, field: Field):
    return ModelField(
        name = name,
        shape = convert_shape(field.shape),
        dtype = convert_dtype(field.type),
        profile = convert_profile(field.profile)
    )