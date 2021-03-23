import logging
from typing import Optional 

import click
from click_aliases import ClickAliasedGroup
from tabulate import tabulate

from hydrosdk import ModelVersion
from hydrosdk.exceptions import TimeoutException
from hydroserving.cli.commands.model import model
from hydroserving.cli.context import CONTEXT_SETTINGS
from hydroserving.cli.context_object import ContextObject


@model.group(cls=ClickAliasedGroup)
def versions(): 
    """
    Working with model versions.
    """
    pass


@versions.command(
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
            'runtime': version.runtime.full,
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
        raise SystemExit(-1)


@versions.command(
    context_settings=CONTEXT_SETTINGS)
@click.option(
    '--id', 'id_', 
    type=int, 
    help="Model version unique identifier")
@click.option(
    '--name-version', 
    type=str, 
    help="Model version reference string in a form name:version")
@click.pass_obj
def logs(obj: ContextObject, id_: int, name_version: str):
    """
    Get build logs from a model version. 
    """
    mv = get_model_version_by_id_or_by_reference_string(obj, id_, name_version)
    logging.info(f"Build logs for the {mv}")
    for l in obj.model_service.get_build_logs(mv.id):
        logging.info(l.data)


@versions.command(
    context_settings=CONTEXT_SETTINGS)
@click.option(
    '--id', 'id_', 
    type=int, 
    help="Model version unique identifier")
@click.option(
    '--name-version', 
    type=str, 
    help="Model version reference string in a form name:version")
@click.option(
    '-i', '--infinity',
    'wait_for_infinity',
    type=bool,
    help="Lock infinitely until the model gets released.",
    is_flag=True,
    default=False)
@click.option(
    '-t', '--timeout',
    type=int,
    help='Timeout after given time, if model doesn\'t get released',
    default=120,)
@click.pass_obj
def lock(obj: ContextObject, id_: int, name_version: str, wait_for_infinity: bool, timeout: str):
    """
    Lock, until the model version gets released.
    """
    mv = get_model_version_by_id_or_by_reference_string(obj, id_, name_version)
    if wait_for_infinity:
        while True:
            try:
                mv.lock_till_released()
                break
            except TimeoutException:
                pass
    else:
        mv.lock_till_released(timeout)



def get_model_version_by_id_or_by_reference_string(obj: ContextObject, id_: int, reference: str) -> ModelVersion:
    """
    A helper function to retrieve a ModelVersion by id or by a reference string.
    """
    if id_ is None and name_version is None:
        logging.error("Either --id or --name-version options should be provided.") 
        raise SystemExit(-1)
    
    if id_ is not None:
        mv = obj.model_service.find_version_by_id(id_)
    else:
        try: 
            name, version = reference.split(':')
        except ValueError as e:
            logging.error("Couldn't parse a model version reference string. "
                "The reference should be in a form `model_name:version`")
            raise SystemExit(-1)
        mv = obj.model_service.find_version(name, version)
    return mv
