from abc import ABC, abstractclassmethod
from hydro_serving_grpc import DT_STRING, DT_BOOL, \
    DT_HALF, DT_FLOAT, DT_DOUBLE, DT_INT8, DT_INT16, \
    DT_INT32, DT_INT64, DT_UINT8, DT_UINT16, DT_UINT32, \
    DT_UINT64, DT_COMPLEX64, DT_COMPLEX128

string = 'string'
boolean = 'boolean'
float64 = 'double'
float32 = 'float32'
int32 = 'int32'
int16 = 'int16'
int8 = 'int8'

HS_DTYPE_TO_ARG_NAME = {
    DT_HALF: "half_val",
    DT_FLOAT: "float_val",
    DT_DOUBLE: "double_val",

    DT_INT8: "int_val",
    DT_INT16: "int_val",
    DT_INT32: "int_val",
    DT_INT64: "int64_val",
    DT_UINT8: "int_val",
    DT_UINT16: "int_val",
    DT_UINT32: "uint32_val",
    DT_UINT64: "uint64_val",
    DT_COMPLEX64: "scomplex_val",
    DT_COMPLEX128: "dcomplex_val",
    DT_BOOL: "bool_val",
    DT_STRING: "string_val",
}


class Field(ABC):
    @abstractclassmethod
    def to_definition(self):
        raise NotImplementedError

    @abstractclassmethod
    def from_request(self, name, v):
        raise NotImplementedError

    @abstractclassmethod
    def to_response(self, name, v):
        raise NotImplementedError
