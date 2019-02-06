import logging
import os
import pprint
import shutil
import tarfile

import click

from hydroserving.config.settings import PACKAGE_CONTRACT_FILENAME, TARGET_FOLDER
from hydroserving.core.model.entities import Model
from hydroserving.core.model.parser import ModelParser
from hydroserving.filesystem.utils import copy_to_target, resolve_list_of_globs, get_yamls


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
        logging.debug("Payload item detected: {}".format(file))
        result_paths.append(file)
    return result_paths


def assemble_model(model, model_path):
    """
    Compresses TARGET_PATH to .tar.gz archive
    Returns path to the archive.

    Args:
        model (Model):
        model_path (str):
    """
    logger = logging.getLogger()
    target_dir = os.path.join(model_path, TARGET_FOLDER)
    hs_model_dir = os.path.join(target_dir, model.name)
    if os.path.exists(hs_model_dir):
        shutil.rmtree(hs_model_dir)
    os.makedirs(hs_model_dir)

    files = resolve_model_payload(model)
    logger.info("Files to assemble: {}".format(files))
    tar_name = "{}.tar.gz".format(model.name)
    tar_path = os.path.join(hs_model_dir, tar_name)
    logging.info("Assembling the model")
    with tarfile.open(tar_path, "w:gz") as tar:
        for entry in files:
            entry_name = os.path.basename(entry)
            logger.debug("Archiving {} as {}".format(entry, entry_name))
            tar.add(entry, arcname=entry_name)
    return tar_path


def ensure_model(dir_path, name, runtime, host_selector, path_to_training_data):
    """

    Args:
        host_selector (str):
        runtime (str):
        dir_path (str):
        name (str):
        path_to_training_data (str or None):

    Returns:
        Model:
    """
    serving_files = [
        file
        for file in get_yamls(dir_path)
        if os.path.splitext(os.path.basename(file))[0] == "serving"
    ]
    serving_file = serving_files[0] if serving_files else None
    logging.debug("Serving YAML definitions: {}".format(serving_files))
    if len(serving_files) > 1:
        logging.warning("Multiple serving files. Using {}".format(serving_file))

    logging.debug("Chosen YAML file: {}".format(serving_file))

    metadata = None
    if serving_file is not None:
        with open(serving_file, 'r') as f:
            metadata = ModelParser().yaml_file(f)
            if name is not None:
                metadata.name = name
            if runtime is not None:
                metadata.runtime = runtime
            if host_selector is not None:
                metadata.host_selector = host_selector
            if path_to_training_data is not None:
                metadata.training_data_file = path_to_training_data

    if metadata is None:
        if name is None:
            name = os.path.basename(os.getcwd())
        metadata = Model(
            name=name,
            contract=None,
            runtime=runtime,
            host_selector=host_selector,
            payload=[os.path.join(dir_path, "*")],
            training_data_file=path_to_training_data,
            install_command=None
        )
    resolve_model_paths(dir_path, metadata)
    logging.info("Model definition composed: {}".format(pprint.pformat(metadata.__dict__, compact=True)))

    metadata.validate()
    return metadata


def resolve_model_paths(dir_path, model):
    """

    Args:
        dir_path (str): path to dir with metadata
        model (Model):

    Returns:
        Model: with resolved payload paths
    """
    abs_payload_paths = []
    for p in model.payload:
        normalized = os.path.expandvars(
            os.path.expanduser(
                os.path.normpath(p)
            )
        )
        if not os.path.isabs(normalized):
            normalized = os.path.normpath(os.path.join(dir_path, normalized))
        abs_payload_paths.append(normalized)

    logging.debug("Resolving payload paths. dir={}, payload={}, resolved={}".format(dir_path,
                                                                                    model.payload,
                                                                                    abs_payload_paths))

    model.payload = abs_payload_paths
    return model
