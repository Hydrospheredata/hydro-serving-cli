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
def app():
    """
    Manage applications.
    """
    pass


@app.command(
    aliases=["ls"],
    context_settings=CONTEXT_SETTINGS)
@click.pass_obj
def list(obj: ContextObject):
    """
    List all applications. 
    """
    view = []
    for app in obj.application_service.list():
        view.append({
            "id": app.id,
            "name": app.name,
            "status": app.status.name,
        })
    if view:
        logging.info(tabulate(view, headers="keys", tablefmt="github"))
    else:
        logging.info("Couldn't find any applications.")
        raise SystemExit(0)


@app.command(
    aliases=["desc"],
    context_settings=CONTEXT_SETTINGS)
@click.argument("name")
@click.pass_obj
def describe(obj: ContextObject, name: str):
    """
    Describe an application.
    """
    app = obj.application_service.find(name)
    logging.info(json.dumps({
        "id": app.id,
        "name": app.name,
        "metadata": app.metadata,
        "executionGraph": app.execution_graph._asdict(),
        "streamingParams": app.kafka_streaming,
        "status": app.status.name,
    }))


@app.command(
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
    Delete an application.
    """
    _ = is_confirmed or click.confirm(
        f"Do you REALLY want to delete the application {name}?", abort=True)
    
    obj.application_service.delete(name)
    logging.info(f"Application {name} has been deleted.")
