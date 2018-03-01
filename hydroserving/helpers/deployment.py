import click
import os

from hydroserving.constants.deployment import RUNTIME_PORT, RUNTIME_MODEL_PATH
from hydroserving.constants.package import PACKAGE_PATH

from hydroserving.helpers.package import pack_model
from hydroserving.helpers.docker import is_container_exists


def start_runtime(metadata, docker_client):
    pack_model(metadata.model)
    click.echo("Deploying model in runtime...")
    deployment_config = metadata.local_deployment
    if is_container_exists(docker_client, deployment_config.name):
        click.echo("'{}' container is already started.".format(deployment_config.name))
        raise SystemExit(-1)
    image = deployment_config.runtime
    docker_client.containers.run(
        str(image),
        remove=True, detach=True,
        name=metadata.local_deployment.name,
        ports={RUNTIME_PORT: metadata.local_deployment.port},
        volumes={os.path.abspath(PACKAGE_PATH): {'bind': RUNTIME_MODEL_PATH, 'mode': 'ro'}}
    )
    click.echo("'{}' container is started.".format(deployment_config.name))


def stop_runtime(metadata, docker_client):
    deployment_config = metadata.local_deployment
    if not is_container_exists(docker_client, deployment_config.name):
        click.echo("'{}' container is not found.".format(deployment_config.name))
        raise SystemExit(-1)
    container = docker_client.containers.get(deployment_config.name)
    container.remove(force=True)
    click.echo("'{}' container is removed".format(deployment_config.name))
