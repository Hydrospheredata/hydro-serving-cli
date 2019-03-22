import click
import logging

from hydroserving.cli.commands.hs import hs_cli
from hydroserving.cli.context import CONTEXT_SETTINGS
from hydroserving.cli.help import PROFILE_HELP, PROFILE_PUSH_HELP, PROFILE_MODEL_VERSION_HELP


@hs_cli.group(help=PROFILE_HELP)
def profile():
    pass


@profile.command(help=PROFILE_PUSH_HELP, context_settings=CONTEXT_SETTINGS)
@click.option('--model-version',
              required=True,
              help=PROFILE_MODEL_VERSION_HELP)
@click.argument('filename',
                type=click.File(mode='rb'))
@click.option('--async', 'is_async', is_flag=True, default=False)
@click.pass_obj
def push(obj, model_version, filename, is_async):
    url = obj.config_service.get_connection()
    if model_version == "~~~":  # only for debugging
        mv = {"model": {"id": 1}, "modelVersion": 1}
        mv_id = 1
    else:
        model, version = model_version.split(":")
        mv = obj.model_service.find_version(model, int(version))
        mv_id = mv["id"]
    obj.monitoring_service.start_data_processing(mv_id, filename)
    logging.info("Data profile for {} will be available: {}/models/{}/{}".format(
        model_version, url, mv["model"]["id"], mv["modelVersion"]))


@profile.command(context_settings=CONTEXT_SETTINGS)
@click.argument('model-version-id',
                required=True)
@click.pass_obj
def status(obj, model_version_id):
    res = obj.monitoring_service.get_data_processing_status(model_version_id)
    logging.info("Data profiling status: %s", res)
