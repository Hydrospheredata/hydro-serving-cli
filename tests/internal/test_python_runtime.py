from hydroserving.python.server import *
import hydroserving.python as hs
import hydro_serving_grpc as hsg

@hs.entrypoint()
@hs.inputs(
    a = hs.Scalar(hs.string)
)
@hs.outputs(
    a = hs.Scalar(hs.string),
    dummy = hs.Scalar(hs.string)
)
def dummy_func(a):
    res = {}
    res['dummy'] = 'kek'
    res['a'] = a
    print(res)
    return res

def test_runtime_status():
    server = dummy_func._serving_server
    servicer = server.servicer
    result = servicer.Status({}, {})
    print(result)
    assert result.status == 1

def test_runtime_predict():
    server = dummy_func._serving_server
    servicer = server.servicer
    request = hsg.PredictRequest(
        inputs = {
            'a': hs.Scalar(hs.string).to_response('a', {'a': 'hello'})
        }
    )
    result = servicer.Predict(request, {})
    print("result", result)
    assert b'kek' == result.outputs['dummy'].string_val[0]