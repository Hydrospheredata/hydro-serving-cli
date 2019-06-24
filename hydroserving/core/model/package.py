import logging
import os
import pprint
import shutil
import tarfile
import glob
import tabulate

from click import ClickException

from hydroserving.config.settings import TARGET_FOLDER, SEGMENT_DIVIDER
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
    runtime = meta_dict.get('runtime')
    logging.info("Parsed model definition")
    logging.info("Name: " + str(meta_dict.get('name')))
    logging.info("Runtime: " + str(runtime.get('name') + ":" + runtime.get('tag')))
    logging.info("Install command: " + str(meta_dict.get('install_command')))
    logging.info("Host selector: " + str(meta_dict.get('host_selector')))
    logging.info("Training data: " + str(meta_dict.get('training_data_file')))
    if (meta_dict.get('contract')):
        logging.info("Signature name: " + str(meta_dict['contract']['predict']['signatureName']))

        logging.info("Inputs:")
        inputs_view = contract_view(meta_dict['contract']['predict']['inputs'])
        logging.info(tabulate.tabulate(inputs_view, headers="keys", tablefmt="github"))

        logging.info("Outputs:")
        outputs_view = contract_view(meta_dict['contract']['predict']['outputs'])
        logging.info(tabulate.tabulate(outputs_view, headers="keys", tablefmt="github"))
    else:
        logging.info("No contract")
    logging.info("Monitoring:")
    logging.info("    " + str(meta_dict.get('monitoring')))
    logging.info("Metadata:")
    for k,v in meta_dict['metadata'].items():
        logging.info("    {}: {}".format(k, v))
    logging.info("Payload:")
    for f in meta_dict['payload']:
        logging.info("    " + str(f))
    logging.info(SEGMENT_DIVIDER)
    model.validate()
    return model

def contract_view(fields):
    outputs_view = []
    for i in fields:
        shape_view = list(map(lambda x: x['size'], i['shape']['dim']))
        if not shape_view:
            shape_view = 'scalar'
        v = {
            'name': i['name'],
            'shape': shape_view,
            'type': i['dtype'],
            'profile': i['profile']
        }
        outputs_view.append(v)
    return outputs_view

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
