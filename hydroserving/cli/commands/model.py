import logging

import click
from click_aliases import ClickAliasedGroup
from tabulate import tabulate

from hydroserving.cli.commands.hs import hs_cli
from hydroserving.cli.context import CONTEXT_SETTINGS
from hydroserving.cli.context_object import ContextObject


@hs_cli.group(cls=ClickAliasedGroup)
def model(): 
    """
    Manage models and model versions.
    """
    pass


@model.command(
    aliases=["ls"], 
    context_settings=CONTEXT_SETTINGS)
@click.pass_obj
def list(obj: ContextObject):
    """
    List models.
    """
    view = []
    for model_id, model_name, versions in obj.model_service.list_models_enriched():
        view.append({
            'id': model_id,
            'name': model_name,
            '# of versions': len([1 for _ in versions]),
        })
    if view:
        logging.info(tabulate(
            sorted(view, key=lambda x: x['name']), 
            headers="keys", 
            tablefmt="github",
        ))
    else:
        logging.info("Couldn't find any models.")
        raise SystemExit(0)


@model.command(
    aliases=["remove", "del", "rm"], 
    context_settings=CONTEXT_SETTINGS)
@click.option(
    '--id', 'id_', 
    type=int, 
    help="Model unique identifier.")
@click.argument("name")
@click.option(
    '-y', '--yes',
    'is_confirmed',
    type=bool,
    is_flag=True,
    default=False,
    help="Proceed without confirmation.")
@click.pass_obj
def delete(obj: ContextObject, id_: int, name: str, is_confirmed: bool):
    """
    Delete a model and all of its versions.
    """
    if id_ is None and name is None:
        logging.error("Either --id option or [NAME] argument should be provided.") 
        raise SystemExit(-1)

    if id_ is None:
        model_id = obj.model_service.find_model_by_name(name)
        num_versions = len(obj.model_service.list_versions_by_model_name(name))
    else:
        model_id = id_
        num_versions = len(obj.model_service.list_versions_by_model_id(model_id))

    _ = is_confirmed or click.confirm(
        f"Do you REALLY want to delete the model {name} and all of its ({num_versions}) versions?", abort=True)
    
    obj.model_service.delete(model_id)
    logging.info(f"Model {name} and all of its ({num_versions}) versions has been deleted.")
