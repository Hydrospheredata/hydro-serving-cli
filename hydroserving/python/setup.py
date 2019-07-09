import setuptools
import sys
import importlib
import inspect
from hydroserving.python.contract_decorators import *
from hydroserving.python.types import *
from hydroserving.cli.context_object import ContextObject
from hydroserving.core.model.entities import UploadMetadata
from hydroserving.core.contract import contract_to_dict


class ModelDefinitionError(Exception):
    pass


def python_runtime(major, minor):
    return "hydrosphere/serving-runtime-python-{major}.{minor}:dev".format(major=major, minor=minor)

def setup(
    name,
    entry_point = None,
    requirements = None,
    runtime = None,
    payload = '.',
    monitoring = None,
    metadata = None,
    host_selector = None):

    python_version = sys.version_info
    if not requirements:
        requirements = []
    if not runtime:
        runtime = python_runtime(python_version[0], python_version[1])
    print("Runtime", runtime)
    if not entry_point:
        raise ModelDefinitionError("Need to set up a prediction endpoint. Use `module:func` format.")
    (entry_module, entry_func) = entry_point.split(':')
    if not monitoring:
        monitoring = []
        
    func = get_entrypoint(entry_module, entry_func)
    print("Entrypoint", func.__name__)
    contract = func._serving_contract
    print("Model contract", contract)

    cmd = sys.argv[1] if len(sys.argv) > 1 else "install"

    if cmd == 'upload':
        upload(name, requirements, entry_point, contract, host_selector, runtime, metadata)
    else:
        install(name, requirements, entry_point)

def install(name, requirements,entrypoint):
    print("INSTALL")
    pkgs = setuptools.find_packages()
    print("SETUP PKGS", pkgs)
    setuptools.setup(
        name=name,
        packages=pkgs,
        include_package_data=True,
        install_requires=requirements,
        entry_points='''
            [console_scripts]
            {name}={entrypoint}._serving_server.start
        '''.format(name=name, entrypoint=entrypoint),
        script_args = ['install'] # pass setup arguments as in `python setup.py install`
    )

def upload(name, requirements, entrypoint, contract, host_selector, runtime, metadata):
    print("UPLOAD")
    pkgs = setuptools.find_packages()
    print("SETUP PKGS", pkgs)
    # create tar.gz source distribution
    setuptools.setup(
        name=name,
        packages=pkgs,
        include_package_data=True,
        install_requires=requirements,
        entry_points='''
            [console_scripts]
            {name}={entrypoint}._serving_server.start
        '''.format(name=name, entrypoint=entrypoint),
        script_args = ['sdist', '--formats=gztar'] # pass setup arguments as in `python setup.py install`
    )
    tar_path = './dist/{name}-0.0.0.tar.gz'.format(name=name)
    context = ContextObject.with_config_path()
    # create model object
    (r_name, r_tag) = runtime.split(':')
    metadata = UploadMetadata(
        name = name,
        contract = contract_to_dict(contract),
        host_selector = host_selector,
        runtime = {
            'name': r_name,
            'tag': r_tag
        },
        install_command = "cd {script_name}-0.0.0 && python serving.py install\nENTRYPOINT {script_name}".format(script_name=name), # Hacky
        metadata = metadata
    )
    context.model_service.upload(tar_path, metadata)

def get_entrypoint(module_path, func_path):
    module = importlib.import_module(module_path)
    named_func = inspect.getmembers(module, lambda a: inspect.isfunction(a) and a.__name__ == func_path)[0]
    return named_func[1]