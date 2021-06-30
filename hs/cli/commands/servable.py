import click

from tabulate import tabulate

from hs.cli.commands.hs import hs_cli
from hs.cli.context import CONTEXT_SETTINGS
from hs.cli.help import PROFILE_HELP, PROFILE_PUSH_HELP, PROFILE_MODEL_VERSION_HELP
from hs.config.cluster_config import get_cluster_connection
from hydrosdk.servable import Servable


@hs_cli.group(help=PROFILE_HELP)
def servable():
    pass


@servable.command(context_settings=CONTEXT_SETTINGS)
def list():
    conn = get_cluster_connection()
    servables = Servable.list(conn)
    
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
def deploy(model_name):
    (name, version) = model_name.split(':')
    version = int(version)
    conn = get_cluster_connection()
    servable = Servable.create(conn, name, version)
    click.echo(f"Servable {servable.name} was created.")

@servable.command(context_settings=CONTEXT_SETTINGS)
@click.argument('servable-name',
                required=True)
@click.option('-y', default=False, is_flag=True)
def rm(servable_name, y):
    if not y:
        click.confirm(f"Are you sure you want to delete the {servable_name} servable?", abort=True)
    conn = get_cluster_connection()
    Servable.delete(conn, servable_name)
    click.echo(f"Servable {servable_name} was deleted")


@servable.command(context_settings=CONTEXT_SETTINGS)
@click.argument('servable-name', required=True)
@click.option('--follow', '-f', required=False, default=False, type=bool, is_flag=True)
def logs(servable_name, follow):
    conn = get_cluster_connection()
    servable = Servable.find_by_name(conn, servable_name)
    logs = servable.logs(follow)
    for event in logs:
        if event:
            click.echo(event.data)
    click.echo("End of logs")

