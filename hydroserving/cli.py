import os

import click
import docker

from hydroserving.constants.package import PACKAGE_PATH
from hydroserving.constants.click import CONTEXT_SETTINGS
from hydroserving.constants.help import *

from hydroserving.models.context_object import ContextObject
from hydroserving.models import FolderMetadata

from hydroserving.helpers.docker import is_container_exists
from hydroserving.helpers.assembly import assemble_model
from hydroserving.helpers.package import pack_model, read_contract
from hydroserving.helpers.upload import upload_model
from hydroserving.helpers.deployment import *


@click.group()
@click.pass_context
def hs_cli(ctx):
    ctx.obj = ContextObject()
    metadata = FolderMetadata.from_directory(os.getcwd())
    ctx.obj.metadata = metadata


@hs_cli.command(help=STATUS_HELP)
@click.pass_obj
def status(obj):
    metadata = obj.metadata
    if metadata is None:
        click.echo("Directory doesn't have a serving metadata")
    else:
        click.echo("Detected a model: {}".format(metadata.model.name))
        click.echo("Model type: {}".format(metadata.model.model_type))
        click.echo("Files to upload:\n{}".format(metadata.model.payload))


@hs_cli.command()
@click.pass_obj
def pack(obj):
    metadata = ensure_metadata(obj)
    payload = pack_model(metadata.model)
    click.echo("Done. Packed: {}".format(payload))


@hs_cli.command()
@click.pass_obj
def assemble(obj):
    metadata = ensure_metadata(obj)
    assemble_model(metadata.model)
    click.echo("Done")


@hs_cli.command()
@click.pass_obj
def contract(obj):
    metadata = ensure_metadata(obj)
    click.echo("Reading contract...")
    contract_obj = read_contract(metadata.model)
    click.echo(contract_obj)


@hs_cli.command(help=UPLOAD_HELP, context_settings=CONTEXT_SETTINGS)
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
@click.option('--source',
              help=UPLOAD_SOURCE_HELP,
              required=False)
@click.pass_obj
def upload(obj, host, port, source):
    metadata = ensure_metadata(obj)
    result = upload_model(host, port, source, metadata.model)
    click.echo(result.json())


# LOCAL DEPLOYMENT COMMANDS

@hs_cli.group(help=LOCAL_HELP)
@click.pass_context
def local(ctx):
    ctx.obj.docker_client = docker.from_env()


@local.command(help=START_HELP)
@click.pass_obj
def start(obj):
    metadata = ensure_metadata(obj)
    click.echo("Deploying model in runtime...")
    docker_client = obj.docker_client
    start_runtime(metadata, docker_client)


@local.command(help=STOP_HELP)
@click.pass_obj
def stop(obj):
    metadata = ensure_metadata(obj)
    docker_client = obj.docker_client
    stop_runtime(metadata, docker_client)


def ensure_metadata(obj):
    if obj.metadata is None:
        click.echo("Directory doesn't have a serving metadata")
        raise SystemExit(-1)
    return obj.metadata
