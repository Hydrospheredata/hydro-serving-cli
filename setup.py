from setuptools import setup, find_packages

with open("version") as v:
    version = v.read()

setup(
    name='hs',
    version=version,
    description="Hydro-serving command line tool",
    author="Hydrospheredata",
    license="Apache 2.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click==6.7",
        "pyyaml~=4.2",
        "protobuf~=3.6",
        "kafka-python==1.4.3",
        "hydro-serving-grpc~=0.2",
        "requests~=2.21",
        "requests-toolbelt==0.8.0",
    ],
    setup_requires=[
        'pytest-runner'
    ],
    test_suite='tests',
    tests_require=[
        'pytest>=3.8.0', 'requests_mock>=1.5.0', 'mock>=2.0.0'
    ],
    entry_points='''
        [console_scripts]
        hs=hydroserving.cli.commands.hs:hs_cli
    '''
)