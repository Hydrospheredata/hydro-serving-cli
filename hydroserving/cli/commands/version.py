import logging
import json
from typing import Optional 

import click
from click_aliases import ClickAliasedGroup
from tabulate import tabulate

from hydrosdk import ModelVersion
from hydrosdk.exceptions import TimeoutException
from hydroserving.cli.commands.model import model
from hydroserving.cli.context import CONTEXT_SETTINGS
from hydroserving.cli.context_object import ContextObject
from hydroserving.util.parseutil import _parse_model_reference


@model.group(
    cls=ClickAliasedGroup,
    context_settings=CONTEXT_SETTINGS)
def version(): 
    """
    Working with model versions.
    """
    pass


@version.command(
    aliases=["ls"], 
    context_settings=CONTEXT_SETTINGS)
@click.option(
    '--name', 
    type=str,
    default=None, 
    help="Show versions only for the defined model.")
@click.pass_obj
def list(obj: ContextObject, name: Optional[str] = None):
    """
    List all model versions on the cluster.
    """
    view = []
    if name is None:
        versions = obj.model_service.list_versions()
    else:
        versions = obj.model_service.list_versions_by_model_name(name)
    for version in versions:
        view.append({
            'id': version.id,
            'name': version.name,
            'version #': version.version,
            'status': version.status,
            'runtime': version.runtime.to_string(),
            'apps': version.applications,
        })
    if view:
        logging.info(tabulate(
            sorted(view, key=lambda x: (x['name'], x['version #'])), 
            headers="keys", 
            tablefmt="github",
        ))
    else:
        logging.info("Couldn't find any models")
        raise SystemExit(1)


@version.command(
    context_settings=CONTEXT_SETTINGS)
@click.option(
    '--id', 'id_', 
    type=int, 
    help="Model version unique identifier")
@click.argument(
    "name", 
    required=False)
@click.pass_obj
def logs(obj: ContextObject, id_: int, name: str):
    """
    Get build logs from a model version. 
    """
    mv = get_model_version_by_id_or_by_reference_string(obj, id_, name)
    logging.info(f"Build logs for {mv}")
    for l in obj.model_service.get_build_logs(mv.id):
        logging.info(l.data)


@version.command(
    aliases=["desc"],
    context_settings=CONTEXT_SETTINGS)
@click.argument(
    "name", 
    required=False)
@click.option(
    '--id', 'id_', 
    type=int, 
    help="Model version unique identifier.")
@click.pass_obj
def describe(obj: ContextObject, name: str, id_: int):
    """
    Describe an application.
    """
    mv = get_model_version_by_id_or_by_reference_string(obj, id_, name)
    logging.info(json.dumps(mv.to_dict()))


@version.command(
    context_settings=CONTEXT_SETTINGS)
@click.argument(
    "name", 
    required=False)
@click.option(
    '--id', 'id_', 
    type=int, 
    help="Model version unique identifier.")
@click.option(
    '-i', '--inf',
    'wait_for_infinity',
    type=bool,
    help="Lock infinitely until the model gets released.",
    is_flag=True,
    default=False)
@click.option(
    '-t', '--timeout',
    type=int,
    help='Timeout after a given time, if model doesn\'t get released.',
    default=120,)
@click.pass_obj
def lock(obj: ContextObject, id_: int, name: str, wait_for_infinity: bool, timeout: str):
    """
    Lock, until the model version gets released.
    """
    mv = get_model_version_by_id_or_by_reference_string(obj, id_, name)
    try:
        if wait_for_infinity:
            while True:
                try:
                    mv.lock_till_released()
                    break
                except TimeoutException:
                    pass
        else:
            mv.lock_till_released(timeout)
    except (ModelVersion.ReleaseFailed, TimeoutException) as e:
        logging.error(e)
        raise SystemExit(1)


def get_model_version_by_id_or_by_reference_string(obj: ContextObject, id_: int, reference: str) -> ModelVersion:
    """
    A helper function to retrieve a ModelVersion by id or by a reference string.
    """
    if id_ is None and reference is None:
        logging.error("Either --id option or [NAME] argument should be provided") 
        raise SystemExit(1)

    if id_ is not None:
        logging.debug(f"Retrieve model version by id: {id_}")
        mv = obj.model_service.find_version_by_id(id_)
    else:
        logging.debug(f"Retrieve model by reference string: {reference}")
        name, version = _parse_model_reference(reference)
        mv = obj.model_service.find_version(name, version)
    return mv
