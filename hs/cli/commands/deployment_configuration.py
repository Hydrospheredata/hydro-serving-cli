import click
from hydrosdk.deployment_configuration import DeploymentConfiguration
from tabulate import tabulate
import textwrap

from hs.cli.commands.hs import hs_cli
from hs.cli.help import DEPLOYMENT_CONFIGURATION_LIST_HELP, \
    DEPLOYMENT_CONFIGURATION_HELP, DEPLOYMENT_CONFIGURATION_RM_HELP
from hs.entities.cluster_config import get_cluster_connection

def wrap_text(text: str) -> str:
    return "\n".join(textwrap.wrap(str(text), width=50))

@hs_cli.group(help=DEPLOYMENT_CONFIGURATION_HELP)
@click.pass_context
def depconf(ctx):
    ctx.obj = get_cluster_connection()

@depconf.command()
@click.argument("depconf-name")
@click.pass_obj
def get(obj, depconf_name):
    deployment_configuration = DeploymentConfiguration.find(obj, depconf_name)
    table = {
        "param": [
            "name",
            "container",
            "pod",
            "deployment",
            "hpa"
            ],
        "value": [
            deployment_configuration.name,
            wrap_text(deployment_configuration.container),
            wrap_text(deployment_configuration.pod),
            wrap_text(deployment_configuration.deployment),
            wrap_text(deployment_configuration.hpa),
        ]
    }
    click.echo(tabulate(table))

@depconf.command(help=DEPLOYMENT_CONFIGURATION_LIST_HELP)
@click.pass_obj
def list(obj):
    click.echo("List of available deployment configurations:")
    deployment_configurations = DeploymentConfiguration.list(obj)
    for config in deployment_configurations:
        click.echo(f"\t* {config}")


@depconf.command(help=DEPLOYMENT_CONFIGURATION_RM_HELP)
@click.argument("depconf-name")
@click.pass_obj
def rm(obj, depconf_name):
    DeploymentConfiguration.delete(obj, depconf_name)
    click.echo("Deployment Configuration '{depconf_name}' removed successfully")
