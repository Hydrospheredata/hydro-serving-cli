import click

from hydroserving.cli import CONTEXT_SETTINGS
from hydroserving.cli.commands.hs import hs_cli
from hydroserving.cli.help import PROFILE_HELP, PROFILE_PUSH_HELP, PROFILE_MODEL_VERSION_HELP


@hs_cli.group(help=PROFILE_HELP)
def profile():
    pass


@profile.command(help=PROFILE_PUSH_HELP, context_settings=CONTEXT_SETTINGS)
@click.option('--model-version',
              required=True,
              help=PROFILE_MODEL_VERSION_HELP)
@click.argument('filename',
                type=click.Path(exists=True))
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
    obj.profiler_service.push_training_data(mv_id, filename, is_async)
    click.echo("Data profile for {} will be available: {}/models/{}/{}".format(
        model_version, url, mv["model"]["id"], mv["modelVersion"]))