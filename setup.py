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
        'click==6.7',
        'docker==3.0.1',
        'pyyaml',
        'kafka-python==1.4.1',
        "hydro-serving-grpc==0.1.1",
        "requests-toolbelt==0.8.0"
    ],
    test_suite='tests',
    entry_points='''
        [console_scripts]
        hs=hydroserving.cli:hs_cli
    '''
)
