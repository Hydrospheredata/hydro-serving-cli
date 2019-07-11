import hydroserving.python as hp

@hp.entrypoint
@hp.inputs(
    a = hp.Scalar('int32', profile="NUMERICAL"),
    b = hp.Scalar('int32', profile="NONE")
)
@hp.outputs(
    s = hs.Scalar('int32', profile="NUMERICAL")
)
def sum(a, b):
    return {
        's': a + b
    }