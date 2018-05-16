import docker

from hydroserving.cli.dev.dev_group import dev
from hydroserving.cli import ensure_metadata
from hydroserving.cli.hs import hs_cli
from hydroserving.constants.help import *
from hydroserving.helpers.deployment import *
from hydroserving.helpers.package import build_model


@dev.group(help=DEV_HELP)
@click.pass_context
def deploy(ctx):
    ctx.obj.docker_client = docker.from_env()


@deploy.command(help=DEV_UP_HELP)
@click.pass_obj
def up(obj):
    metadata = ensure_metadata(obj)
    click.echo("Deploying model in runtime...")
    docker_client = obj.docker_client
    build_model(metadata)
    start_runtime(metadata, docker_client)


@deploy.command(help=DEV_DOWN_HELP)
@click.pass_obj
def down(obj):
    metadata = ensure_metadata(obj)
    docker_client = obj.docker_client
    stop_runtime(metadata, docker_client)