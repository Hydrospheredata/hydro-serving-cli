import click
import requests
import os

from hydroserving.cli.hs import hs_cli
from hydroserving.cli.utils import ensure_cluster, ensure_model
from hydroserving.constants.help import CONTEXT_SETTINGS, UPLOAD_HELP
from hydroserving.helpers.upload import upload_model
from hydroserving.httpclient.api import ModelAPI
from hydroserving.httpclient.remote_connection import RemoteConnection


@hs_cli.command(help=UPLOAD_HELP, context_settings=CONTEXT_SETTINGS)
@click.option('--name',
              default=os.path.basename(os.getcwd()),
              show_default=True,
              required=False)
@click.option('--model_type',
              default="unknown",
              required=False)
@click.option('--contract',
              type=click.Path(exists=True),
              default=None,
              required=False)
@click.option('--description',
              default=None,
              required=False)
@click.pass_obj
def upload(obj, name, model_type, contract, description):
    current_cluster = ensure_cluster(obj)
    click.echo("Using '{}' cluster".format(current_cluster['name']))
    remote = RemoteConnection(current_cluster['cluster']['server'])
    model_api = ModelAPI(remote)

    model = ensure_model(obj, os.getcwd(), name, model_type, description, contract)

    try:
        result = upload_model(model_api, model)
        click.echo("Success response:")
        click.echo(result)
    except requests.RequestException as err:
        click.echo()
        click.echo("Upload failed. Reason:")
        click.echo(err)
        raise SystemExit(-1)
