import hydro_serving_grpc as hsg
from hydro_serving_grpc import DT_STRING, DT_BOOL, \
    DT_HALF, DT_FLOAT, DT_DOUBLE, DT_INT8, DT_INT16, \
    DT_INT32, DT_INT64, DT_UINT8, DT_UINT16, DT_UINT32, \
    DT_UINT64, DT_COMPLEX64, DT_COMPLEX128
from google.protobuf.json_format import MessageToDict
from hydroserving.python.types.base import Field, HS_DTYPE_TO_ARG_NAME
from hydroserving.core.contract import NAME_TO_DTYPES
import numpy as np

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

class Array(Field):
    def __init__(self, type, shape, profile = None):
        self.type = type
        self.shape = shape
        self.dtype = NAME_TO_DTYPES[type]
        self.numpy_type = HS_TO_NP_DTYPE[self.dtype]
        if profile:
            self.profile = profile
        else:
            self.profile = "NONE"
    
    def to_definition(self):
        field_def = {
            'type': self.type,
            'shape': self.shape,
            'profile': self.profile
        }
        return field_def

    def from_request(self, name, v):
        data = v[name]
        raw_result = data.__getattribute__(HS_DTYPE_TO_ARG_NAME[self.dtype])
        if data.dtype == hsg.DT_STRING:
            raw_result = [x.decode('utf-8') for x in raw_result]
        result = np.array(raw_result, dtype=self.numpy_type).reshape(self.shape)
        return result

    def to_response(self, name, v):
        data = v[name]
        if self.dtype == hsg.DT_STRING:
            data = [x.encode('utf-8') for x in data]
        kwargs = {
            HS_DTYPE_TO_ARG_NAME[self.dtype]: data.flatten(),
            "dtype": hsg.DataType.Name(self.dtype),
            "tensor_shape": hsg.TensorShapeProto(dim=[hsg.TensorShapeProto.Dim(size=x) for x in self.shape])
        }
        return hsg.TensorProto(**kwargs)
