import time

import click

from hydroserving.cli import ensure_cluster
from hydroserving.cli.hs import hs_cli
from hydroserving.constants.help import PROFILE_HELP, PROFILE_PUSH_HELP, PROFILE_MODEL_VERSION_HELP, CONTEXT_SETTINGS
from hydroserving.helpers.upload import create_bar_callback_factory
from hydroserving.httpclient.api import ProfilesAPI, ModelAPI
from hydroserving.httpclient.remote_connection import RemoteConnection


@hs_cli.group(help=PROFILE_HELP)
def profile():
    pass


@profile.command(help=PROFILE_PUSH_HELP, context_settings=CONTEXT_SETTINGS)
@click.option('--model-version',
              required=True,
              help=PROFILE_MODEL_VERSION_HELP)
@click.argument('filename', type=click.Path(exists=True))
@click.pass_obj
def push(obj, model_version, filename):
    current_cluster = ensure_cluster(obj)
    click.echo("Using '{}' cluster".format(current_cluster['name']))
    url = current_cluster['cluster']['server']
    remote = RemoteConnection(url)
    profile_api = ProfilesAPI(remote)
    if model_version == "~~~":  # only for debugging
        mv = {"model": {"id": 1}, "modelVersion": 1}
        mv_id = 1
    else:
        model, version = model_version.split(":")
        model_api = ModelAPI(remote)
        mv = model_api.find_version(model, int(version))
        mv_id = mv["id"]
    with click.progressbar(length=1, label='Uploading training data') as bar:
        uid = profile_api.push(mv_id, filename, create_bar_callback_factory(bar))
        click.echo()
        click.echo("Data profile computing is started with id {}".format(uid))
        status = ""
        while status != "success":
            status = profile_api.status(uid)
            time.sleep(30)
        click.echo("Data profile for {} is ready: {}/models/{}/{}".format(
            model_version, url, mv["model"]["id"], mv["modelVersion"]))
