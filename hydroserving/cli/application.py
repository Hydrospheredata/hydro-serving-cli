import click
import os
from hydroserving.cli.hs import hs_cli
from hydroserving.cli.utils import ensure_app_data
from hydroserving.constants.help import APPLICATION_HELP, UPLOAD_HOST_HELP, UPLOAD_PORT_HELP
from hydroserving.httpclient.api import ApplicationAPI
from hydroserving.httpclient.remote_connection import RemoteConnection
from hydroserving.models.application import Application


@hs_cli.group(help=APPLICATION_HELP)
@click.pass_obj
def app(obj):
    obj.app_data = Application.from_directory(os.getcwd())


@app.command()
@click.option('--host',
              default="localhost",
              show_default=True,
              help=UPLOAD_HOST_HELP,
              required=False)
@click.option('--port',
              default=9090,
              show_default=True,
              help=UPLOAD_PORT_HELP,
              required=False)
@click.pass_obj
def deploy(obj, host, port):
    app = ensure_app_data(obj)
    remote = RemoteConnection("http://{}:{}".format(host, port))
    app_api = ApplicationAPI(remote)
    app_api.list()
    click.echo(app.__dict__)


@app.command()
@click.option('--host',
              default="localhost",
              show_default=True,
              help=UPLOAD_HOST_HELP,
              required=False)
@click.option('--port',
              default=9090,
              show_default=True,
              help=UPLOAD_PORT_HELP,
              required=False)
@click.pass_obj
def list(obj, host, port):
    remote = RemoteConnection("http://{}:{}".format(host, port))
    app_api = ApplicationAPI(remote)
    apps = app_api.list()
    click.echo(apps)
    raise NotImplementedError()