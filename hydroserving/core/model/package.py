import logging
import os
import pprint
import shutil
import tarfile

from hydroserving.config.settings import TARGET_FOLDER
from hydroserving.core.contract import contract_to_dict
from hydroserving.integrations.dvc_extractor import collect_dvc_info, dvc_to_dict
from hydroserving.integrations.git_extractor import collect_git_info, git_to_dict
from hydroserving.core.image import DockerImage
from hydroserving.core.model.entities import Model
from hydroserving.core.model.parser import parse_model
from hydroserving.util.fileutil import resolve_list_of_globs, get_yamls
from hydroserving.util.dictutil import extract_dict
from hydroserving.util.yamlutil import yaml_file


def resolve_model_payload(model):
    result_paths = []
    files = resolve_list_of_globs(model.payload)
    for file in files:
        logging.debug("Payload item detected: %s", file)
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
    logger.info("Files to assemble: %s", files)
    tar_name = "{}.tar.gz".format(model.name)
    tar_path = os.path.join(hs_model_dir, tar_name)
    logging.debug("Creating archive: %s", tar_path)
    with tarfile.open(tar_path, "w:gz") as tar:
        for entry in files:
            entry_name = os.path.basename(entry)
            logger.debug("Archiving %s as %s", entry, entry_name)
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
    logging.debug("Serving YAML definitions: %s", serving_files)
    if len(serving_files) > 1:
        logging.warning("Multiple serving files. Using %s", serving_file)

    logging.debug("Chosen YAML file: %s", serving_file)

    model = None
    if serving_file is not None:
        with open(serving_file, 'r') as f:
            doc = yaml_file(f)
            model = parse_model(doc)
            if name is not None:
                model.name = name
            if runtime is not None:
                model.runtime = DockerImage.parse_fullname(runtime)
            if host_selector is not None:
                model.host_selector = host_selector
            if path_to_training_data is not None:
                model.training_data_file = path_to_training_data

    if model is None:
        if name is None:
            name = os.path.basename(os.getcwd())
        if runtime is None:
            raise ValueError("Runtime is not defined. Please use YAML config or CLI argument to set it.")
        model = Model(
            name=name,
            contract=None,
            runtime=DockerImage.parse_fullname(runtime),
            host_selector=host_selector,
            payload=[os.path.join(dir_path, "*")],
            training_data_file=path_to_training_data,
            install_command=None,
            monitoring=None,
            metadata={}
        )
    resolve_model_paths(dir_path, model)
    gitinfo = collect_git_info(dir_path, search_parent_directories=True)
    if gitinfo:
        logging.debug("Extracted git metadata: %s", gitinfo)
        model.metadata.update(git_to_dict(gitinfo))

    dvcinfo = collect_dvc_info(dir_path)
    if dvcinfo:
        logging.debug("Extracted dvc metadata: %s", dvcinfo)
        model.metadata.update(dvc_to_dict(dvcinfo))

    meta_dict = extract_dict(model)
    meta_dict['contract'] = contract_to_dict(meta_dict['contract'])
    logging.info("Model definition composed:")
    logging.info(pprint.pformat(meta_dict, compact=True, ))
    model.validate()
    return model


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

    logging.debug("Resolving payload paths. dir=%s, payload=%s, resolved=%s",
                  dir_path,
                  model.payload,
                  abs_payload_paths)

    model.payload = abs_payload_paths
    return model
