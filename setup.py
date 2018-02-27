from setuptools import setup, find_packages

with open("version") as v:
    version = v.read()

setup(
    name='hs',
    version=version,
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click==6.7',
        'docker==3.0.1',
        'pyyaml',
        "hydro-serving-grpc==0.0.13"
    ],
    entry_points='''
        [console_scripts]
        hs=hydroserving.cli:hs_cli
    '''
)
