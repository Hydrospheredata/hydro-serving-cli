import click
from hydroserving.cli.hs import hs_cli
from hydroserving.cli.utils import ensure_metadata
from hydroserving.helpers.assembly import assemble_model
from hydroserving.helpers.package import read_contract_cwd
from hydroserving.helpers.upload import upload_model
from hydroserving.httpclient.api import ModelAPI
from hydroserving.constants.help import STATUS_HELP, CONTEXT_SETTINGS, UPLOAD_HELP,UPLOAD_HOST_HELP, UPLOAD_PORT_HELP, UPLOAD_SOURCE_HELP
from hydroserving.httpclient.remote_connection import RemoteConnection


@hs_cli.command(help=STATUS_HELP)
@click.pass_obj
def status(obj):
    metadata = ensure_metadata(obj)
    click.echo("Detected a model: {}".format(metadata.model.name))
    click.echo("Model type: {}".format(metadata.model.model_type))
    click.echo("Files to upload:\n{}".format(metadata.model.payload))

@hs_cli.command()
@click.pass_obj
def contract(obj):
    metadata = ensure_metadata(obj)
    click.echo("Reading contract...")
    contract_obj = read_contract_cwd(metadata.model)
    click.echo(contract_obj)


@hs_cli.command(help=UPLOAD_HELP, context_settings=CONTEXT_SETTINGS)
@click.option('--host',
              default="localhost",
              show_default=True,
              help=UPLOAD_HOST_HELP,
              required=False)
@click.option('--port',
              default=80,
              show_default=True,
              help=UPLOAD_PORT_HELP,
              required=False)
@click.pass_obj
def upload(obj, host, port):
    metadata = ensure_metadata(obj)
    remote = RemoteConnection("http://{}:{}".format(host, port))
    model_api = ModelAPI(remote)
    result = upload_model(model_api, metadata.model)
    click.echo()
    click.echo(result)
