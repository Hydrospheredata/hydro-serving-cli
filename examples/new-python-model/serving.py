from hydroserving.python import setup

setup(
    name='calculator',
    requirements=[
        "hydro-serving-grpc~=2.0",
    ],
    entry_point='src.main:sum'
)
