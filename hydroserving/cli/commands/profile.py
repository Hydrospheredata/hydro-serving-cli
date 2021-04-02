import os
import logging
from typing import Optional

import click

from hydroserving.cli.commands.hs import hs_cli
from hydroserving.cli.context import CONTEXT_SETTINGS
from hydroserving.cli.context_object import ContextObject
from hydroserving.util.parseutil import _parse_model_reference
from hydroserving.cli.commands.version import get_model_version_by_id_or_by_reference_string
from hydroserving.util.err_handler import handle_cluster_error

from hydrosdk.modelversion import DataUploadResponse


@hs_cli.group()
def profile():
    """
    Manage data profiles.
    """
    pass


@profile.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    '--id', 'id_', 
    type=int, 
    help="Model version unique identifier.")
@click.option(
    "--name",
    help="Model version reference string.")
@click.argument(
    "uri",
    required=True)
@click.option(
    '--async', 
    'is_async', 
    is_flag=True, 
    default=False)
@click.option(
    "--retry",
    type=int,
    default=12,
    help="How many times to retry polling, if profiling is not yet finished. Defaults to 12.")
@click.option(
    "--sleep",
    type=int,
    default=30,
    help="Sleep time between retries. Defaults to 30.")
@click.pass_obj
def upload(
        obj: ContextObject, 
        id_: Optional[int], 
        name: Optional[str], 
        uri: str, 
        is_async: bool,
        retry: int,
        sleep: int,
):
    """
    Upload a training dataset to compute its profiles.
    """
    mv = get_model_version_by_id_or_by_reference_string(obj, id_, name)
    logging.info(f"Uploading training data for '{mv.name}:{mv.version}'")
    mv.training_data = uri
    dur = handle_cluster_error(mv.upload_training_data)()
    if not is_async:
        dur.wait(retry=retry, sleep=sleep)


@profile.command(
    context_settings=CONTEXT_SETTINGS)
@click.option(
    '--id', 'id_', 
    type=int, 
    help="Model version unique identifier.")
@click.option(
    "--name",
    help="Model version reference string.")
@click.option(
    "--retry",
    type=int,
    default=12,
    help="How many times to retry polling, if profiling is not yet finished. Defaults to 12.")
@click.option(
    "--sleep",
    type=int,
    default=30,
    help="Sleep time between retries. Defaults to 30.")
@click.pass_obj
def lock(obj: ContextObject, id_: int, name: str, retry: int, sleep: int):
    """
    Lock, until the profiling job gets completed.
    """
    mv = get_model_version_by_id_or_by_reference_string(obj, id_, name)
    dur = DataUploadResponse(mv.cluster, mv.id)
    try:
        dur.wait(retry, sleep)
    except (DataUploadResponse.NotRegistered, DataUploadResponse.Failed) as e:
        logging.error(e)
