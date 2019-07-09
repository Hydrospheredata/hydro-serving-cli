class Field:
    def to_definition(self):
        raise NotImplementedError

class Scalar:
    def __init__(self, type, profile = None):
        self.type = type
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

class Array:
    def __init__(self, type, shape, profile = None):
        self.type = type
        self.shape = shape
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



string = 'string'
boolean = 'boolean'
double = 'double'
float = 'float'
int32 = 'int32'
int16 = 'int16'
int8 = 'int8'