import unittest
import hydroserving.python as hs

@hs.entrypoint
@hs.inputs(
    a = hs.Scalar(hs.int32),
    b = hs.Scalar(hs.int32),
)
@hs.outputs(s = hs.Scalar(hs.int32))
def model_scalar(a, b):
    return {
        's': a + b
    }

@hs.entrypoint
@hs.inputs(v = hs.Array(hs.double, shape=[-1]))
@hs.outputs(s = hs.Scalar(hs.double))
def model_vec(v):
    return {
        's': len(v)
    }

def test_injected_attrs():
    scalar_sig = model_scalar._serving_contract.predict
    vec_sig = model_vec._serving_contract.predict
    assert scalar_sig is not None
    assert vec_sig is not None