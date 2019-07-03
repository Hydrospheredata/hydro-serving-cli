import unittest
import hydroserving.internals.contract.python_model as hs

@hs.entrypoint
@hs.input('a', 'int32')
@hs.input('b', 'int32')
@hs.output('s', 'int32')
def model_scalar(a, b):
    return {
        's': a + b
    }

@hs.entrypoint
@hs.input('v', 'double', shape=[-1])
@hs.output('s', 'int32')
def model_vec(v):
    return {
        's': len(v)
    }

class TestDecorators(unittest.TestCase):
    def test_injected_attrs(self):
        scalar_sig = model_scalar._serving_contract.predict
        vec_sig = model_vec._serving_contract.predict
        assert scalar_sig is not None
        assert vec_sig is not None