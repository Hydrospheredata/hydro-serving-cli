import click
import os
import shutil
import tarfile

from hydroserving.constants.package import PACKAGE_CONTRACT_PATH
from hydroserving.constants.package import TARGET_PATH, PACKAGE_FILES_PATH
from hydroserving.helpers.contract import read_contract_cwd


def get_files(path):
    """
    Recursively lists files
    :param path: Path to look for
    :return: flat list of files
    """
    return [
        os.path.join(dir_name, file)
        for dir_name, _, files in os.walk(path)
        for file in files
    ]


def get_visible_files(path):
    """
    Recursively lists visible files
    :param path: Path to look for
    :return: flat list of visible files
    """
    return [
        os.path.join(dir_name, file)
        for dir_name, _, files in os.walk(path)
        for file in files
        if not file.startswith('.')
    ]


def get_payload_files(payload):
    """
    Iterates over payload paths and recursively retrieves visible files
    :param payload: list of paths
    :return: flat list of visible files
    """
    files = []
    for x in payload:
        if os.path.isfile(x):
            files.append(x)
        else:
            sub_files = get_visible_files(x)
            for sub_file in sub_files:
                files.append(sub_file)
    return files


def copy_to_target(src_path):
    """
    Copies path to TARGET_PATH
    :param src_path: path to copy
    :return: copied path
    """
    model_dirs = os.path.dirname(src_path)
    packed_dirs = os.path.join(PACKAGE_FILES_PATH, model_dirs)
    if not os.path.exists(packed_dirs):
        os.makedirs(packed_dirs)
    packed_path = os.path.join(PACKAGE_FILES_PATH, src_path)
    shutil.copy(src_path, packed_path)
    return packed_path


def pack_payload(model):
    """
    Moves payload to TARGET_PATH
    :param model: ModelDefinition
    :return: list of copied files
    """
    if not os.path.exists(PACKAGE_FILES_PATH):
        os.makedirs(PACKAGE_FILES_PATH)

    files = get_payload_files(model.payload)

    copied_files = []
    with click.progressbar(iterable=files,
                           item_show_func=lambda x: x,
                           label='Packing the model') as bar:
        for entry in bar:
            copied_file = copy_to_target(entry)
            copied_files.append(copied_file)

    return copied_files


def pack_contract(model):
    """
    Reads a user contract and writes binary version to TARGET_PATH
    :param model: ModelDefinition
    :return: path to written contract
    """
    contract = read_contract_cwd(model)
    contract_destination = os.path.join(PACKAGE_CONTRACT_PATH)

    with open(contract_destination, "wb") as contract_file:
        contract_file.write(contract.SerializeToString())

    return contract_destination


def pack_model(model):
    """
    Copies payload and contract to TARGET_PATH
    :param model: ModelDefinition
    :return: list of copied payload files
    """
    if os.path.exists(TARGET_PATH):
        shutil.rmtree(TARGET_PATH)
    os.mkdir(TARGET_PATH)
    payload_files = pack_payload(model)
    if model.contract_path is not None:
        pack_contract(model)
    return payload_files


def with_cwd(new_cwd, func, *args):
    """
    Wrapper util to run some function in new Current Working Directory
    :param new_cwd: path to the new CWD
    :param func: callback
    :param args: args to the `func`
    :return: result of `func`
    """
    old_cwd = os.getcwd()
    try:
        os.chdir(new_cwd)
        result = func(*args)
        return result
    except Exception as err:
        raise err
    finally:
        os.chdir(old_cwd)


def build_model(metadata):
    """
    Model build for local development purposes
    :param metadata: FolderMetadata
    :return: nothing
    """
    build_steps = metadata.local_deployment.build

    def _execute_build_steps():
        idx = 1
        for build_step in build_steps:
            click.echo("[{}] {}".format(idx, build_step))
            os.system(build_step)
            idx += 1

    if build_steps is None or not build_steps:
        click.echo("No build steps. Skipping...")
        return None

    click.echo("Build steps detected. Executing...")
    with_cwd(TARGET_PATH, _execute_build_steps)
    click.echo("Done.")


def assemble_model(model):
    """
    Compresses TARGET_PATH to .tar.gz archive
    :param model:
    :return:
    """
    files = pack_model(model)
    package_name = "{}.tar.gz".format(model.name)
    package_path = os.path.join(TARGET_PATH, package_name)
    with click.progressbar(iterable=files,
                           item_show_func=lambda x: x,
                           label='Assembling the model') as bar:
        with tarfile.open(package_path, "w:gz") as tar:
            tar_name = tar.name
            for entry in bar:
                relative_name = os.path.relpath(entry, PACKAGE_FILES_PATH)
                tar.add(entry, arcname=relative_name)

    return tar_name
