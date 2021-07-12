import click

from tabulate import tabulate

from hs.cli.commands.hs import hs_cli
from hs.cli.context import CONTEXT_SETTINGS
from hs.entities.cluster_config import get_cluster_connection
from hydrosdk.servable import Servable


@hs_cli.group()
@click.pass_context
def servable(ctx):
    ctx.obj = get_cluster_connection()


@servable.command(context_settings=CONTEXT_SETTINGS)
@click.pass_obj
def list(obj):
    servables = Servable.list(obj)
    
    servables_view = []
    for m in servables:
        servables_view.append({
            'name': m.name,
            'status': m.status,
            'message': m.status_message,
        })
    click.echo(tabulate(sorted(servables_view, key = lambda x: x['name']), headers="keys", tablefmt="github"))

@servable.command(context_settings=CONTEXT_SETTINGS)
@click.argument('model-name', required=True)
@click.pass_obj
def deploy(obj, model_name):
    (name, version) = model_name.split(':')
    version = int(version)
    servable = Servable.create(obj, name, version)
    click.echo(f"Servable {servable.name} was created.")

@servable.command(context_settings=CONTEXT_SETTINGS)
@click.argument('servable-name',
                required=True)
@click.option('-y', default=False, is_flag=True)
@click.pass_obj
def rm(obj, servable_name, y):
    if not y:
        click.confirm(f"Are you sure you want to delete the {servable_name} servable?", abort=True)
    Servable.delete(obj, servable_name)
    click.echo(f"Servable {servable_name} was deleted")


@servable.command(context_settings=CONTEXT_SETTINGS)
@click.argument('servable-name', required=True)
@click.option('--follow', '-f', required=False, default=False, type=bool, is_flag=True)
@click.pass_obj
def logs(obj, servable_name, follow):
    servable = Servable.find_by_name(obj, servable_name)
    logs = servable.logs(follow)
    for event in logs:
        if event:
            click.echo(event.data)
    click.echo("End of logs")

