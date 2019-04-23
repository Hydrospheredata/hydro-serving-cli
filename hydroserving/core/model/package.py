import logging
import os
import pprint
import shutil
import tarfile
import glob

from click import ClickException

from hydroserving.config.settings import TARGET_FOLDER
from hydroserving.core.contract import contract_to_dict
from hydroserving.core.model.entities import Model
from hydroserving.integrations.dvc import collect_dvc_info, dvc_to_dict
from hydroserving.integrations.git import collect_git_info, git_to_dict
from hydroserving.util.dictutil import extract_dict


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

    tar_name = "{}.tar.gz".format(model.name)
    tar_path = os.path.join(hs_model_dir, tar_name)
    logging.debug("Creating archive: %s", tar_path)
    with tarfile.open(tar_path, "w:gz") as tar:
        for entry in model.payload:
            entry_name = os.path.basename(entry)
            logger.debug("Archiving %s as %s", entry, entry_name)
            tar.add(entry, arcname=entry_name)
    return tar_path


def enrich_and_normalize(dir_path, model):
    """

    Args:
        model (Model):
        dir_path (str):

    Returns:
        Model:
    """
    if os.path.isfile(dir_path):
        dir_path = os.path.dirname(dir_path)
        logging.debug("Applying file. Dirname {}".format(dir_path))
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
        unglobbed = glob.glob(normalized)
        for path in unglobbed:
            abs_payload_paths.append(path)
        logging.debug("Payload {} is resolved as {}".format(p, normalized))

    for p in abs_payload_paths:
        if not os.path.exists(p):
            raise ClickException("Model payload path {} doesn't exist".format(p))

    model.payload = abs_payload_paths
    return model
