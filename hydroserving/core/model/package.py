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

from hydrosdk.modelversion import ModelVersionBuilder
from hydrosdk.signature import ModelField
from hydro_serving_grpc.serving.contract.types_pb2 import DataProfileType, DataType


def assemble_model_on_local_fs(builder: ModelVersionBuilder):
    """
    Compresses TARGET_PATH to .tar.gz archive
    Returns path to the archive.
    """
    target_dir = os.path.join(builder.path, TARGET_FOLDER)
    hs_model_dir = os.path.join(target_dir, builder.name)
    if os.path.exists(hs_model_dir):
        shutil.rmtree(hs_model_dir)
    os.makedirs(hs_model_dir)

    tar_name = "{}.tar.gz".format(builder.name)
    tar_path = os.path.join(hs_model_dir, tar_name)
    logging.debug("Creating archive: %s", tar_path)
    with tarfile.open(tar_path, "w:gz") as tar:
        for entry in builder.payload.values():
            source = os.path.join(builder.path, entry)
            entry_name = os.path.basename(entry)
            logging.debug("Archiving %s as %s", source, entry_name)
            tar.add(source, arcname=entry_name)
    return tar_path


def enrich_and_normalize(builder: ModelVersionBuilder) -> ModelVersionBuilder:
    """
    Enrich the model with the additional information contained in the directory.

    :param builder: an instance of a ModelVersionBuilder
    :return: an enriched instance of a ModelVersionBuilder
    """
    path = builder.path
    if os.path.isfile(path):
        path = os.path.dirname(builder.path)
        logging.debug("Applying file. Dirname {}".format(path))
    gitinfo = collect_git_info(path, search_parent_directories=True)
    if gitinfo:
        logging.debug("Extracted git metadata: %s", gitinfo)
        builder.metadata.update(git_to_dict(gitinfo))
    dvcinfo = collect_dvc_info(path)
    if dvcinfo:
        logging.debug("Extracted dvc metadata: %s", dvcinfo)
        builder.metadata.update(dvc_to_dict(dvcinfo))
    logging.info("Parsed a model definition")
    logging.info(SEGMENT_DIVIDER)
    logging.info("Name: " + builder.name)
    logging.info("Runtime: " + builder.runtime.to_string())
    if builder.install_command is not None:
        logging.info("Install command: " + builder.install_command)
    if builder.training_data is not None:
        logging.info("Training data: " + builder.training_data)
    logging.info("Signature name: " + builder.signature.signature_name)
    logging.info("Inputs:")
    inputs_view = _signature_view(builder.signature.inputs)
    logging.info(tabulate.tabulate(inputs_view, headers="keys", tablefmt="github"))
    logging.info("Outputs:")
    outputs_view = _signature_view(builder.signature.outputs)
    logging.info(tabulate.tabulate(outputs_view, headers="keys", tablefmt="github"))
    if builder.monitoring_configuration is not None:
        logging.info("Monitoring:")
        for key, value in builder.monitoring_configuration.to_dict().items():
            logging.info(f"    {key}={value}")
    if builder.metadata is not None and builder.metadata: 
        logging.info("Metadata:")
        for k,v in builder.metadata.items():
            logging.info("    {}: {}".format(k, v))
    logging.info("Payload:")
    for f in builder.payload.values():
        logging.info("    " + str(f))
    logging.info(SEGMENT_DIVIDER)
    return builder


def _signature_view(fields: List[ModelField]) -> List[Dict[str, Any]]:
    outputs_view = []
    for field in fields:
        view = {
            'name': field.name,
            'shape': field.shape.dims or "scalar",
            'profile': DataProfileType.Name(field.profile),
        }
        if hasattr(field, 'dtype'):
            view['type'] = DataType.Name(field.dtype) 
        else:
            view['subfields'] = '...'
        outputs_view.append(view)
    return outputs_view
