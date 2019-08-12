import hydroserving.python as hp


def init():
    print("Initializing model")

    
@hp.entrypoint(on_init=init)
@hp.inputs(
    a = hp.Scalar('int32', profile="NUMERICAL"),
    b = hp.Scalar('int32', profile="NONE")
)
@hp.outputs(
    s = hp.Scalar('int32', profile="NUMERICAL")
)
def sum(a, b):
    return {
        's': a + b
    }
