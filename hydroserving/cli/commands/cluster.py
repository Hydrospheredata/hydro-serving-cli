import logging

import click

from hydroserving.cli.commands.hs import hs_cli
from hydroserving.cli.help import CLUSTER_HELP, CLUSTER_USE_HELP, CLUSTER_LIST_HELP, CLUSTER_ADD_HELP, \
    CLUSTER_RM_HELP


@hs_cli.group(
    invoke_without_command=True,
    help=CLUSTER_HELP
)
@click.pass_context
def cluster(ctx):
    if ctx.invoked_subcommand is None:
        logging.info("Current cluster: {}".format(ctx.obj.config_service.current_cluster()))


@cluster.command(help=CLUSTER_USE_HELP)
@click.argument('cluster_name')
@click.pass_obj
def use(obj, cluster_name):
    res = obj.config_service.select_cluster(cluster_name)
    if res is not None:
        logging.info("Switched to cluster '{}'".format(cluster_name))
    else:
        logging.error("Can't find cluster '{}'".format(cluster_name))
        raise SystemExit(-1)


@cluster.command(help=CLUSTER_LIST_HELP)
@click.pass_obj
def list(obj):
    logging.info("Clusters:")
    clusters = obj.config_service.list_clusters()
    for cluster in clusters:
        click.echo(cluster)


@cluster.command(help=CLUSTER_ADD_HELP)
@click.option('--name', required=True)
@click.option('--server', required=True)
@click.pass_obj
def add(obj, name, server):
    try:
        res = obj.config_service.add_cluster(name, server)
        if res is not None:
            logging.info("Cluster '{}' @ {} added successfully".format(name, server))
        else:
            logging.error("There is already a cluster named '{}'".format(name))
            raise SystemExit(-1)
    except ValueError as err:
        logging.error("Cluster validation error: {}".format(err))
        raise SystemExit(-1)


@cluster.command(help=CLUSTER_RM_HELP)
@click.argument("cluster_name")
@click.pass_obj
def rm(obj, cluster_name):
    res = obj.config_service.remove_cluster(cluster_name)
    if res is not None:
        logging.info("Cluster '{}' removed successfully".format(cluster_name))
    else:
        logging.error("There is no '{}' cluster".format(cluster_name))
        raise SystemExit(-1)
