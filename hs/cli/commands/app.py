
import click
from tabulate import tabulate

from hs.cli.commands.hs import hs_cli
from hs.cli.context import CONTEXT_SETTINGS
from hs.cli.help import PROFILE_HELP
from hs.entities.cluster_config import get_cluster_connection
from hydrosdk.application import Application

@hs_cli.group(help=PROFILE_HELP)
@click.pass_context
def app(ctx):
    ctx.obj = get_cluster_connection(ctx.obj)


@app.command(context_settings=CONTEXT_SETTINGS)
@click.pass_obj
def list(obj):
    apps = Application.list(obj)
    apps_view = []
    for a in apps:
        apps_view.append({'name': a.name})
    click.echo(tabulate(apps_view, headers="keys", tablefmt="github"))


@app.command(context_settings=CONTEXT_SETTINGS)
@click.argument('app-name',
                required=True)
@click.option('-y', default=False, is_flag=True)
@click.pass_obj
def rm(obj, app_name, y):
    if not y:
        click.confirm(f"Are you sure you want to delete the {app_name} application?", abort=True)
    Application.delete(obj, app_name)
    click.echo(f"Application is  deleted: {app_name}")
