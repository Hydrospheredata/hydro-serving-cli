from hydroserving.python import setup

setup(
    name='calculator',
    description="Example of a Python model",
    requirements=[
        "hydro-serving-grpc~=2.0",
    ],
    entry_point='src.main:sum'
)