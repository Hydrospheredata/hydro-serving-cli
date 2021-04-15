import logging
import json

import click
from click_aliases import ClickAliasedGroup
from tabulate import tabulate

from hydroserving.cli.commands.hs import hs_cli
from hydroserving.cli.context import CONTEXT_SETTINGS
from hydroserving.cli.context_object import ContextObject


@hs_cli.group(
    cls=ClickAliasedGroup)
def servable():
    """
    Manage servables.
    """
    pass


@servable.command(
    aliases=["ls"],
    context_settings=CONTEXT_SETTINGS)
@click.pass_obj
def list(obj: ContextObject):
    """
    List servables.
    """
    view = []
    for servable in obj.servable_service.list():
        depconfig = servable.deployment_configuration.name if servable.deployment_configuration else ""
        view.append({
            'name': servable.name,
            'application': servable.meta.get('applicationName', ''),
            'deployment configuration': depconfig,
            'status': servable.status.name,
            'message': servable.status_message,
        })
    if view:
        logging.info(tabulate(
            sorted(view, key=lambda x: x['name']), 
            headers="keys", 
            tablefmt="github",
        ))
    else:
        logging.info("Couldn't find any servables")


@servable.command(
    aliases=["del", "remove", "rm"],
    context_settings=CONTEXT_SETTINGS)
@click.argument("name")
@click.option(
    '-y', '--yes',
    'is_confirmed',
    type=bool,
    is_flag=True,
    default=False,
    help="Proceed without confirmation.")
@click.pass_obj
def delete(obj: ContextObject, name: str, is_confirmed: bool):
    """
    Delete a servable.
    """
    _ = is_confirmed or click.confirm(
        f"Do you REALLY want to delete the servable '{name}'?", abort=True)
    
    obj.servable_service.delete(name)
    logging.info(f"Servable '{name}' has been deleted")


@servable.command(
    aliases=["desc"],
    context_settings=CONTEXT_SETTINGS)
@click.argument("name")
@click.pass_obj
def describe(obj: ContextObject, name: str):
    """
    Describe a deployment configuration.
    """
    servable = obj.servable_service.find(name)
    logging.info(json.dumps(servable.to_dict()))


@servable.command(
    context_settings=CONTEXT_SETTINGS)
@click.argument(
    'name', 
    required=True)
@click.option(
    '-f', '--follow', 
    required=False, 
    default=False, 
    type=bool, 
    is_flag=True)
@click.pass_obj
def logs(obj: ContextObject, name: str, follow: bool):
    """
    Get logs of a servable.
    """
    iterator = obj.servable_service.logs(name, follow)
    if iterator:
        for event in iterator:
            if event:
                logging.info(event.data.rstrip())
    else:
        logging.error(f"Cannot fetch logs for servable '{name}'")
        raise SystemExit(1)
