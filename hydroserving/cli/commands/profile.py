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
@click.option('--filename',
              type=click.File(mode='rb'),
              required=False
              )
@click.option('--s3path',
              type=click.STRING,
              required=False)
@click.option('--async', 'is_async', is_flag=True, default=False)
@click.pass_obj
def push(obj, model_version, filename, s3path, is_async):
    url = obj.config_service.get_connection()
    if model_version == "~~~":  # only for debugging
        mv = {"model": {"id": 1}, "modelVersion": 1}
        mv_id = 1
    else:
        model, version = model_version.split(":")
        mv = obj.model_service.find_version(model, int(version))
        mv_id = mv["id"]
    if s3path:
        logging.info("S3 training path detected.")
        resp = obj.monitoring_service.push_s3_csv(mv_id, s3path)
        logging.debug(resp)
    elif filename:
        resp = obj.monitoring_service.start_data_processing(mv_id, filename)
        logging.debug(resp)
    else:
        raise click.ClickException("Neither S3 nor file was defined.")
    logging.info("Data profile for {} will be available: {}/models/{}/{}".format(
        model_version, url.remote_addr, mv["model"]["id"], mv["id"]))


@profile.command(context_settings=CONTEXT_SETTINGS)
@click.argument('model-version',
                required=True)
@click.pass_obj
def status(obj, model_version):
    model, version = model_version.split(":")
    mv = obj.model_service.find_version(model, int(version))
    if not mv:
        raise click.ClickException("Model {} is not found".format(model_version))
    mv_id = mv['id']
    res = obj.monitoring_service.get_data_processing_status(mv_id)
    logging.info("Looking for profiling status for model id=%s name=%s version=%s", mv_id, model, version)
    logging.info("Data profiling status: %s", res)
