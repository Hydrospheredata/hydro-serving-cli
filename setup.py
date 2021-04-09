from setuptools import setup, find_packages

with open("version", 'r') as v:
    version = v.read().strip()

setup(
    name='hs',
    version=version,
    description="Hydro-serving command line tool",
    author="Hydrospheredata",
    license="Apache 2.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click~=7.1.2",
        "click-log~=0.3",
        "click-aliases~=1.0.1",
        "pyyaml~=5.3",
        "protobuf~=3.6",
        "kafka-python==1.4.3",
        "hydro-serving-grpc>=3.0.0-dev3",
        "requests~=2.23.0",
        "requests-toolbelt~=0.9",
        "gitpython~=2.1",
        "tabulate~=0.8",
        "hydrosdk~=3.0.0-dev1",
        "sseclient-py ~=1.7",
    ],
    python_requires=">=3.6",
    setup_requires=['pytest-runner'],
    test_suite='tests',
    tests_require=[
        'pytest>=3.8.0',
        'requests_mock>=1.5.0',
        'mock>=2.0.0'
    ],
    entry_points='''
        [console_scripts]
        hs=hydroserving.cli.commands.hs:hs_cli
    '''
)
