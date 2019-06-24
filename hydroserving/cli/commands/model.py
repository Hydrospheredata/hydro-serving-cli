import click
import logging

from tabulate import tabulate

from hydroserving.cli.commands.hs import hs_cli
from hydroserving.cli.context import CONTEXT_SETTINGS
from hydroserving.cli.help import PROFILE_HELP, PROFILE_PUSH_HELP, PROFILE_MODEL_VERSION_HELP


@hs_cli.group(help=PROFILE_HELP)
def model():
    pass


@model.command(context_settings=CONTEXT_SETTINGS)
@click.pass_obj
def list(obj):
    models = obj.model_service.list_versions()
    if models:
        versions_view = []
        for m in models:
            model = m.get('model')
            runtime = m.get('runtime')
            versions_view.append({
                'id': m.get('id'),
                'name': model.get('name'),
                '#': m.get('modelVersion'),
                'status': m.get('status'),
                'runtime': "{}:{}".format(runtime.get('name'), runtime.get('tag')),
                'apps': m.get('applications')
            })
        logging.info(tabulate(sorted(versions_view, key = lambda x: (x['name'], x['#'])), headers="keys", tablefmt="github"))
    else:
        logging.warning("Can't get model version list: %s", models)
        raise SystemExit(-1)


@model.command(context_settings=CONTEXT_SETTINGS)
@click.argument('model-name',
                required=True)
@click.pass_obj
def rm(obj, model_name):
    mv = obj.model_service.find_model(model_name)
    if not mv:
        raise click.ClickException("Model {} not found".format(model_name))
    mv_id = mv['id']
    res = obj.model_service.delete(mv_id)
    logging.info("Model and it's versions are deleted: %s", res)

@model.command(context_settings=CONTEXT_SETTINGS)
@click.argument('model-name', required=True)
@click.pass_obj
def logs(obj, model_name):
    (name, version) = model_name.split(':')
    mv = obj.model_service.find_version(name, version)
    if not mv:
        raise click.ClickException("Model {} not found".format(model_name))
    mv_id = mv['id']
    logs = obj.model_service.get_logs(mv_id)
    if not logs:
        raise click.ClickException("No logs found")
    for l in logs:
        logging.info(l.data)