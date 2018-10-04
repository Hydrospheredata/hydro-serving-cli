import os
import pprint
import click
import requests

from hydroserving.cli.hs import hs_cli
from hydroserving.cli.utils import ensure_cluster, create_or_ensure_model
from hydroserving.constants.help import CONTEXT_SETTINGS, UPLOAD_HELP, APPLY_HELP
from hydroserving.constants.package import TARGET_FOLDER
from hydroserving.helpers.upload import upload_model
from hydroserving.httpclient.api import ModelAPI
from hydroserving.httpclient.remote_connection import RemoteConnection
from hydroserving.parsers.abstract import ParserError
from hydroserving.services.apply import ApplyService, ApplyError


@hs_cli.command(help=UPLOAD_HELP, context_settings=CONTEXT_SETTINGS)
@click.option('--name',
              default=os.path.basename(os.getcwd()),
              show_default=True,
              required=False)
@click.option('--model_type',
              default=None,
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

    model = create_or_ensure_model(os.getcwd(), name, model_type, description, contract)
    obj.model = model

    try:
        result = upload_model(model_api, model, TARGET_FOLDER)
        click.echo("Success response:")
        click.echo(result)
    except requests.RequestException as err:
        click.echo()
        click.echo("Upload failed. Reason:")
        click.echo(err)
        raise SystemExit(-1)


@hs_cli.command(help=APPLY_HELP, context_settings=CONTEXT_SETTINGS)
@click.option('-f',
              type=click.Path(exists=True),
              multiple=True,
              required=True)
@click.option('--ignore-monitoring',
              type=bool,
              required=False,
              default=False,
              is_flag=True)
@click.pass_obj
def apply(obj, f, ignore_monitoring):
    http_service = obj.services.http
    apply_service = ApplyService(http_service)
    try:
        click.echo("Using current cluster at {}".format(http_service.connection.remote_addr))
        result = apply_service.apply(f, ignore_monitoring=ignore_monitoring)
        click.echo(pprint.pformat(result))
    except ApplyError as ex:
        click.echo("Error while applying {}".format(f))
        click.echo(ex)
        raise SystemExit(-1)
    except ParserError as ex:
        click.echo("Error while applying: {}".format(f))
        click.echo(ex)
        raise SystemExit(-1)
