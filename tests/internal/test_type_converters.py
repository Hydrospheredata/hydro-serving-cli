from hydroserving.python.types import *
import numpy as np

RESPONSE_DATA = {
    'a': 2.0,
    'b': ['hello', 'world'],
    'c': np.random.uniform(size=6).reshape([-1, 3])
}

def test_scalar_type():
    s = Scalar(float32)
    resp = s.to_response('a', RESPONSE_DATA)
    print(resp)
    assert resp.float_val[0] == 2.0
    assert resp.dtype == hsg.DT_FLOAT
    req = { 'a': resp }
    res = s.from_request('a', req)
    assert res == 2.0

def test_list_type():
    s = List(string)
    resp = s.to_response('b', RESPONSE_DATA)
    print(resp)
    assert resp.string_val == [b'hello', b'world']
    assert resp.dtype == hsg.DT_STRING
    req = { 'b': resp }
    res = s.from_request('b', req)
    assert res == ['hello', 'world']


def test_numpy_array_type():
    s = Array(float64, shape=[-1, 3])
    resp = s.to_response('c', RESPONSE_DATA)
    print(resp)
    assert resp.double_val == RESPONSE_DATA['c'].flatten().tolist()
    assert resp.dtype == hsg.DT_DOUBLE
    req = { 'c': resp }
    res = s.from_request('c', req)
    print(res)
    assert res.flatten().tolist() == RESPONSE_DATA['c'].flatten().tolist()
    assert res.shape == (2, 3)