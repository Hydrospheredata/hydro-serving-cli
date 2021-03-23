import logging
import os
import shutil
import tarfile
import glob
import tabulate
from typing import List, Dict, Any

import click
from click import ClickException

from hydroserving.config.settings import TARGET_FOLDER, SEGMENT_DIVIDER
from hydroserving.integrations.dvc import collect_dvc_info, dvc_to_dict
from hydroserving.integrations.git import collect_git_info, git_to_dict

from hydrosdk.modelversion import LocalModel
from hydrosdk.signature import ModelField


def assemble_model(dir_path: str, local_model: LocalModel):
    """
    Compresses TARGET_PATH to .tar.gz archive
    Returns path to the archive.

    Args:
        model (Model):
        model_path (str):
    """
    target_dir = os.path.join(dir_path, TARGET_FOLDER)
    hs_model_dir = os.path.join(target_dir, local_model.name)
    if os.path.exists(hs_model_dir):
        shutil.rmtree(hs_model_dir)
    os.makedirs(hs_model_dir)

    tar_name = "{}.tar.gz".format(local_model.name)
    tar_path = os.path.join(hs_model_dir, tar_name)
    logging.debug("Creating archive: %s", tar_path)
    with tarfile.open(tar_path, "w:gz") as tar:
        for entry in local_model.payload.values():
            entry_name = os.path.basename(entry)
            logging.debug("Archiving %s as %s", entry, entry_name)
            tar.add(entry, arcname=entry_name)
    return tar_path


def enrich_and_normalize(dir_path: str, local_model: LocalModel) -> LocalModel:
    """
    Enrich the model with the additional information contained in the directory.

    :param dir_path: a path, where model artifacts are located
    :param local_model: an instance of a LocalModel
    :return: an enriched instance of a LocalModel
    """
    if os.path.isfile(dir_path):
        dir_path = os.path.dirname(dir_path)
        logging.debug("Applying file. Dirname {}".format(dir_path))
    gitinfo = collect_git_info(dir_path, search_parent_directories=True)
    if gitinfo:
        logging.debug("Extracted git metadata: %s", gitinfo)
        local_model.metadata.update(git_to_dict(gitinfo))
    dvcinfo = collect_dvc_info(dir_path)
    if dvcinfo:
        logging.debug("Extracted dvc metadata: %s", dvcinfo)
        local_model.metadata.update(dvc_to_dict(dvcinfo))
    logging.info("Parsed model definition")
    logging.info("Name: " + local_model.name)
    logging.info("Runtime: " + str(local_model.runtime))
    if local_model.install_command is not None:
        logging.info("Install command: " + local_model.install_command)
    if local_model.training_data is not None:
        logging.info("Training data: " + local_model.training_data)
    logging.info("Signature name: " + local_model.signature.signature_name)
    logging.info("Inputs:")
    inputs_view = signature_view(local_model.signature.inputs)
    logging.info(tabulate.tabulate(inputs_view, headers="keys", tablefmt="github"))
    logging.info("Outputs:")
    outputs_view = signature_view(local_model.signature.outputs)
    logging.info(tabulate.tabulate(outputs_view, headers="keys", tablefmt="github"))
    if local_model.monitoring_configuration is not None:
        logging.info("Monitoring:")
        logging.info("    " + str(local_model.monitoring_configuration))
    if local_model.metadata is not None: 
        logging.info("Metadata:")
        for k,v in local_model.metadata.items():
            logging.info("    {}: {}".format(k, v))
    logging.info("Payload:")
    for f in local_model.payload.values():
        logging.info("    " + str(f))
    logging.info(SEGMENT_DIVIDER)
    return local_model


def signature_view(fields: List[ModelField]) -> List[Dict[str, Any]]:
    outputs_view = []
    for field in fields:
        view = {
            'name': field.name,
            'shape': field.shape or "scalar",
            'profile': field.profile
        }
        if hasattr(field, 'dtype'):
            view['type'] = field.dtype
        else:
            view['subfields'] = '...'
        outputs_view.append(view)
    return outputs_view
