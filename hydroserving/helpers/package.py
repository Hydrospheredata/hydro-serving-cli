import glob
import os
import shutil
import tarfile

import click

from hydroserving.constants.package import TARGET_FOLDER, PACKAGE_CONTRACT_FILENAME, PACKAGE_FILES_DIR
from hydroserving.models.definitions.model import Model


def get_payload_files(payload):
    """
    Iterates over payload paths and recursively retrieves visible files

    Args:
        payload (list of str):

    Returns:
        dict: key - parent path of file, value - files within parent component

    """
    paths = []
    for glob_path in payload:
        expanded = os.path.expanduser(glob_path)
        unglobbed = glob.glob(expanded)
        for path in unglobbed:
            if os.path.exists(path):
                paths.append(path)
            else:
                raise ValueError("Path {} doesn't exist".format(path))
    return paths


def copy_to_target(src_path, package_path):
    """
    Copies path to TARGET_PATH

    Args:
        src_path (str):
        package_path (str):
    """
    basename = os.path.basename(src_path)

    packed_path = os.path.join(package_path, basename)
    if os.path.isfile(src_path):
        shutil.copy(src_path, packed_path)
    elif os.path.isdir(src_path):
        shutil.copytree(src_path, packed_path)
    else:
        raise FileNotFoundError(src_path)
    return packed_path


def pack_payload(model, package_path):
    """
    Moves payload to target_path

    Args:
        model Model:
        package_path str:
    """

    if not os.path.exists(package_path):
        os.makedirs(package_path)

    files = get_payload_files(model.payload)
    print(files)
    result_paths = []
    with click.progressbar(iterable=files,
                           item_show_func=lambda x: x,
                           label='Packing the model') as bar:
        for file in bar:
            copied_path = copy_to_target(file, package_path)
            result_paths.append(copied_path)

    return result_paths


def pack_contract(model, package_path):
    """
    Reads a user contract and writes binary version to TARGET_PATH
    :param model: ModelDefinition
    :return: path to written contract
    """
    contract_destination = os.path.join(package_path, PACKAGE_CONTRACT_FILENAME)

    with open(contract_destination, "wb") as contract_file:
        contract_file.write(model.contract.SerializeToString())

    return contract_destination


def pack_model(model, package_path):
    """
    Copies payload and contract to TARGET_PATH
    Args:
        package_path (str):
        model (Model):

    Returns:

    """
    payload_files = pack_payload(model, package_path)
    if model.contract is not None:
        pack_contract(model, package_path)
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


def assemble_model(model, target_path):
    """
    Compresses TARGET_PATH to .tar.gz archive

    Args:
        model (Model):
        target_path (str):
    """
    hs_model_dir = os.path.join(target_path, model.name)
    if os.path.exists(hs_model_dir):
        shutil.rmtree(hs_model_dir)
    os.makedirs(hs_model_dir)
    package_path = os.path.join(hs_model_dir, PACKAGE_FILES_DIR)
    files = pack_model(model, package_path)

    tar_name = "{}.tar.gz".format(model.name)
    tar_path = os.path.join(target_path, model.name, tar_name)
    with click.progressbar(iterable=files,
                           item_show_func=lambda x: x,
                           label='Assembling the model') as bar:
        with tarfile.open(tar_path, "w:gz") as tar:
            tar_name = tar.name
            for entry in bar:
                relative_name = os.path.relpath(entry, package_path)
                tar.add(entry, arcname=relative_name)

    return tar_name
