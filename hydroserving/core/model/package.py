import os
import shutil
import tarfile

import click

from hydroserving.config.settings import PACKAGE_CONTRACT_FILENAME, PACKAGE_FILES_DIR
from hydroserving.core.model.model import Model
from hydroserving.filesystem.utils import copy_to_target, resolve_list_of_globs


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
    :param package_path
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


def resolve_model_payload(model):
    result_paths = []

    files = resolve_list_of_globs(model.payload)
    for file in files:
        result_paths.append(os.path.basename(file))
    return result_paths


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

    files = resolve_model_payload(model)

    tar_name = "{}.tar.gz".format(model.name)
    tar_path = os.path.join(hs_model_dir, tar_name)
    with click.progressbar(iterable=files,
                           item_show_func=lambda x: x,
                           label='Assembling the model') as bar:
        with tarfile.open(tar_path, "w:gz") as tar:
            for entry in bar:
                tar.add(entry)

    return tar_path
