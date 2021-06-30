
import click
from tabulate import tabulate

from hs.cli.commands.hs import hs_cli
from hs.cli.context import CONTEXT_SETTINGS
from hs.cli.help import PROFILE_HELP
from hs.config.settings import CONFIG_PATH

from hs.config.cluster_config import get_cluster_connection
from hydrosdk.application import Application

@hs_cli.group(help=PROFILE_HELP)
def app():
    pass


@app.command(context_settings=CONTEXT_SETTINGS)
def list():
    conn = get_cluster_connection(CONFIG_PATH)
    apps = Application.list(conn)

    apps_view = []
    for a in apps:
        apps_view.append({'name': a.name})
    click.echo(tabulate(apps_view, headers="keys", tablefmt="github"))


@app.command(context_settings=CONTEXT_SETTINGS)
@click.argument('app-name',
                required=True)
@click.option('-y', default=False, is_flag=True)
def rm(app_name, y):
    if not y:
        click.confirm(f"Are you sure you want to delete the {app_name} application?", abort=True)
    conn = get_cluster_connection()
    Application.delete(conn, app_name)
    click.echo(f"Application is  deleted: {app_name}")
