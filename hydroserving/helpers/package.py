import os
import shutil
import tarfile

import click

from hydroserving.constants.package import TARGET_FOLDER, PACKAGE_CONTRACT_FILENAME, PACKAGE_FILES_DIR
from hydroserving.helpers.file import get_visible_files
from hydroserving.models.definitions.model import Model


def get_payload_files(payload):
    """
    Iterates over payload paths and recursively retrieves visible files

    Args:
        payload (list of str):

    Returns:
        dict: key - parent path of file, value - files within parent component

    """
    files = {}
    for x in payload:
        if os.path.isfile(x):
            parent_dir = os.path.dirname(x)
            if parent_dir not in files:
                files[parent_dir] = []
            files[parent_dir].append(os.path.relpath(x, parent_dir))
        elif os.path.isdir(x):
            sub_files = get_visible_files(x, recursive=True)
            if x not in files:
                files[x] = []
            for sub_file in sub_files:
                files[x].append(os.path.relpath(sub_file, x))
        else:
            raise ValueError("Path {} doesn't exist".format(x))
    return files


def copy_to_target(src_parent, src_path, package_path):
    """
    Copies path to TARGET_PATH

    Args:
        src_parent (str):
        src_path (str):
        package_path (str):
    """

    model_dirs = os.path.dirname(src_path)
    packed_dirs = os.path.join(package_path, model_dirs)
    if not os.path.exists(packed_dirs):
        os.makedirs(packed_dirs)

    packed_path = os.path.join(package_path, src_path)
    original_src_path = os.path.join(src_parent, src_path)
    shutil.copy(original_src_path, packed_path)
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
    all_files = [f
                 for x in files
                 for f in x]
    copied_files = []
    with click.progressbar(length=len(all_files),
                           item_show_func=lambda x: x,
                           label='Packing the model') as bar:
        for parent, sub_files in files.items():
            for file in sub_files:
                copied_file = copy_to_target(parent, file, package_path)
                copied_files.append(copied_file)
                bar.update(1)

    return copied_files


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
    with_cwd(TARGET_FOLDER, _execute_build_steps)
    click.echo("Done.")


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
