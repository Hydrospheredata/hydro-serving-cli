import logging
import json

import click
from click_aliases import ClickAliasedGroup
from tabulate import tabulate

from hydroserving.cli.commands.hs import hs_cli
from hydroserving.cli.context import CONTEXT_SETTINGS
from hydroserving.cli.context_object import ContextObject


@hs_cli.group(
    cls=ClickAliasedGroup,
    context_settings=CONTEXT_SETTINGS)
def config():
    """
    Manage deployment configurations.
    """
    pass


@config.command(
    aliases=["ls"],
    context_settings=CONTEXT_SETTINGS)
@click.pass_obj
def list(obj: ContextObject):
    """
    List all deployment configurations.
    """
    view = [{"name": dc.name} for dc in obj.deployment_configuration_service.list()]
    if view:
        logging.info(tabulate(
            view,
            headers="keys",
            tablefmt="github",
        ))
    else:
        logging.info("Couldn't find any deployment configuration")


@config.command(
    aliases=["desc"],
    context_settings=CONTEXT_SETTINGS)
@click.argument("name")
@click.pass_obj
def describe(obj: ContextObject, name: str):
    """
    Describe a deployment configuration.
    """
    dc = obj.deployment_configuration_service.find(name)
    logging.info(json.dumps(dc.to_dict()))


@config.command(
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
def delete(obj, name: str, is_confirmed: bool):
    """
    Delete a deployment configuration.
    """
    _ = is_confirmed or click.confirm(
        f"Do you REALLY want to delete the deployment configuration '{name}'?", abort=True)
    
    obj.deployment_configuration_service.delete(name)
    logging.info(f"Deployment configuration '{name}' has been deleted")
