import click

from hydroserving.cli import ensure_cluster
from hydroserving.cli.hs import hs_cli
from hydroserving.constants.help import PROFILE_HELP, PROFILE_PUSH_HELP, PROFILE_MODEL_VERSION_HELP, CONTEXT_SETTINGS
from hydroserving.helpers.upload import push_training_data
from hydroserving.httpclient.api import ProfilerAPI, ModelAPI
from hydroserving.httpclient.remote_connection import RemoteConnection


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
    current_cluster = ensure_cluster(obj)
    click.echo("Using '{}' cluster".format(current_cluster['name']))
    url = current_cluster['cluster']['server']
    remote = RemoteConnection(url)
    profile_api = ProfilerAPI(remote)
    if model_version == "~~~":  # only for debugging
        mv = {"model": {"id": 1}, "modelVersion": 1}
        mv_id = 1
    else:
        model, version = model_version.split(":")
        model_api = ModelAPI(remote)
        mv = model_api.find_version(model, int(version))
        mv_id = mv["id"]
    push_training_data(profile_api, mv_id, filename, is_async)
    click.echo("Data profile for {} will be available: {}/models/{}/{}".format(
        model_version, url, mv["model"]["id"], mv["modelVersion"]))
