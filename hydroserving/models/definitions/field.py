from hydro_serving_grpc import DT_INVALID, DT_STRING, DT_BOOL, \
    DT_HALF, DT_FLOAT, DT_DOUBLE, DT_INT8, DT_INT16, \
    DT_INT32, DT_INT64, DT_UINT8, DT_UINT16, DT_UINT32, \
    DT_UINT64, DT_QINT8, DT_QINT16, DT_QINT32, DT_QUINT8, DT_QUINT16, DT_VARIANT

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


class Field:
    def __init__(self, name, stype, shape, profile_type, **kwargs):
        if not isinstance(name, str):
            raise TypeError("name is not a string", type(name))
        self.name = name

        if not isinstance(stype, str):
            raise TypeError("stype is not a string", type(stype))
        self.stype = stype

        self.dtype = NAME_TO_DTYPES.get(stype)
        if self.dtype is None:
            raise ValueError("dtype is not recognized as DataType", self.dtype)

        if not isinstance(shape, list):
            raise TypeError("shape is not a list", type(shape))
        self.shape = shape

        if not isinstance(profile_type, str):
            raise TypeError("profile_type is not a string", type(profile_type))
        self.profile_type = profile_type

        self.misc_attrs = kwargs
