import hydro_serving_grpc as hsg
from hydroserving.python.types.base import Field, HS_DTYPE_TO_ARG_NAME
from google.protobuf.json_format import MessageToDict
from hydroserving.core.contract import NAME_TO_DTYPES

class Scalar(Field):
    def __init__(self, type, profile = None):
        self.type = type
        self.dtype = NAME_TO_DTYPES[type]
        if profile:
            self.profile = profile
        else:
            self.profile = "NONE"

    def to_definition(self):
        field_def = {
            'type': self.type,
            'shape': "scalar",
            'profile': self.profile
        }
        return field_def

    def from_request(self, name, v):
        data = v[name]
        result = data.__getattribute__(HS_DTYPE_TO_ARG_NAME[self.dtype])[0]
        if data.dtype == hsg.DT_STRING:
            result = result.decode('utf-8')
        return result

    def to_response(self, name, v):
        data = v[name]
        if self.dtype == hsg.DT_STRING:
            print("RESPONSE DATA", data)
            data = data.encode('utf-8')
        kwargs = {
            HS_DTYPE_TO_ARG_NAME[self.dtype]: [data],
            "dtype": hsg.DataType.Name(self.dtype)
        }
        return hsg.TensorProto(**kwargs)

class List:
    def __init__(self, type, profile = None):
        self.type = type
        self.dtype = NAME_TO_DTYPES[type]
        if profile:
            self.profile = profile
        else:
            self.profile = "NONE"
    
    def to_definition(self):
        field_def = {
            'type': self.type,
            'shape': [-1],
            'profile': self.profile
        }
        return field_def

    def from_request(self, name, v):
        data = v[name]
        result = data.__getattribute__(HS_DTYPE_TO_ARG_NAME[self.dtype])
        if data.dtype == hsg.DT_STRING:
            result = [x.decode('utf-8') for x in result]
        return result

    def to_response(self, name, v):
        data = v[name]
        if self.dtype == hsg.DT_STRING:
            data = [x.encode('utf-8') for x in data]
        kwargs = {
            HS_DTYPE_TO_ARG_NAME[self.dtype]: data,
            "dtype": hsg.DataType.Name(self.dtype),
            "tensor_shape": hsg.TensorShapeProto(dim=[hsg.TensorShapeProto.Dim(size=-1)])
        }
        return hsg.TensorProto(**kwargs)