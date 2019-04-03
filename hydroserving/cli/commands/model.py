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
                'name': model.get('name'),
                'v': m.get('modelVersion'),
                'status': m.get('status'),
                'runtime': "{}:{}".format(runtime.get('name'), runtime.get('tag')),
                'apps': m.get('applications')
            })
        logging.info(tabulate(sorted(versions_view, key = lambda x: (x['name'], x['v'])), headers="keys", tablefmt="github"))
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
        raise click.ClickException("Model {} is not found".format(model_name))
    mv_id = mv['id']
    res = obj.model_service.delete(mv_id)
    logging.info("Model and it's versions are deleted: %s", res)
