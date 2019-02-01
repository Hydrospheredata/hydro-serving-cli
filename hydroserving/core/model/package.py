import glob
import os
import shutil
import tarfile

import click

from hydroserving.config.settings import TARGET_FOLDER, PACKAGE_CONTRACT_FILENAME, PACKAGE_FILES_DIR
from hydroserving.filesystem.utils import copy_to_target, resolve_list_of_globs
from hydroserving.core.model.model import Model

def pack_payload(model, package_path):
    """
    Moves payload to target_path

    Args:
        model Model:
        package_path str:
    """

    if not os.path.exists(package_path):
        os.makedirs(package_path)

    files = resolve_list_of_globs(model.payload)
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


def resolve_model_payload(model, target_path):
    result_paths = []

    files = resolve_list_of_globs(model.payload)
    for file in files:
            basename = os.path.basename(file)
            relative_path = os.path.join(target_path, basename)
            result_paths.append(relative_path)


def assemble_model(model, target_path):
    """
    Compresses TARGET_PATH to .tar.gz archive
    Returns path to the archive.

    Args:
        model (Model):
        target_path (str):
    """
    hs_model_dir = os.path.join(target_path, model.name)
    if os.path.exists(hs_model_dir):
        shutil.rmtree(hs_model_dir)
    os.makedirs(hs_model_dir)
    package_path = os.path.join(hs_model_dir, PACKAGE_FILES_DIR)
    files = resolve_model_payload(model, package_path)

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

    return tar_path