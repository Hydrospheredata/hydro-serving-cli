import click
import logging

from tabulate import tabulate

from hydroserving.cli.commands.hs import hs_cli
from hydroserving.cli.context import CONTEXT_SETTINGS
from hydroserving.cli.help import PROFILE_HELP, PROFILE_PUSH_HELP, PROFILE_MODEL_VERSION_HELP


@hs_cli.group(help=PROFILE_HELP)
def app():
    pass


@app.command(context_settings=CONTEXT_SETTINGS)
@click.pass_obj
def list(obj):
    apps = obj.application_service.list()
    if apps:
        apps_view = []
        for a in apps:
            apps_view.append({
                'name': a.get('name'),
                'streaming-params': a.get('kafkaStreaming')
            })
        logging.info(tabulate(apps_view, headers="keys", tablefmt="github"))
    else:
        logging.warning("Can't get application list: %s", apps)
        raise SystemExit(-1)


@app.command(context_settings=CONTEXT_SETTINGS)
@click.argument('app-name',
                required=True)
@click.pass_obj
def rm(obj, app_name):
    app = obj.application_service.find(app_name)
    if not app:
        raise click.ClickException("Application {} is not found".format(app_name))
    res = obj.application_service.delete(app_name)
    logging.info("Application is  deleted: %s", res)
