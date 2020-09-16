import logging

import click

from hydroserving.cli.commands.hs import hs_cli
from hydroserving.cli.help import DEPLOYMENT_CONFIGURATION_LIST_HELP, \
    DEPLOYMENT_CONFIGURATION_HELP, DEPLOYMENT_CONFIGURATION_RM_HELP


@hs_cli.group(help=DEPLOYMENT_CONFIGURATION_HELP)
def deployment_configuration():
    pass


@deployment_configuration.command(help=DEPLOYMENT_CONFIGURATION_LIST_HELP)
@click.pass_obj
def list(obj):
    logging.info("List of available deployment configurations:")
    deployment_configurations = obj.deployment_configuration_service.list()
    for config in deployment_configurations:
        click.echo(f"\t* {config}")


@deployment_configuration.command(help=DEPLOYMENT_CONFIGURATION_RM_HELP)
@click.argument("deployment-configuration-name")
@click.pass_obj
def rm(obj, deployment_configuration_name):
    res = obj.deployment_configuration_service.delete(deployment_configuration_name)
    if res is not None:
        logging.info("Deployment Configuration '{}' removed successfully".format(deployment_configuration_name))
    else:
        logging.error("There is no '{}' deployment configuration".format(deployment_configuration_name))
        raise SystemExit(-1)
