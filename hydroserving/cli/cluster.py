import click

from hydroserving.cli.hs import hs_cli
from hydroserving.constants.help import CLUSTER_HELP, CLUSTER_USE_HELP, CLUSTER_LIST_HELP, CLUSTER_ADD_HELP, \
    CLUSTER_RM_HELP


@hs_cli.group(
    invoke_without_command=True,
    help=CLUSTER_HELP
)
@click.pass_context
def cluster(ctx):
    if ctx.invoked_subcommand is None:
        click.echo("Current cluster: {}".format(ctx.obj.services.config.current_cluster()))


@cluster.command(help=CLUSTER_USE_HELP)
@click.argument('cluster_name')
@click.pass_obj
def use(obj, cluster_name):
    res = obj.services.config.select_cluster(cluster_name)
    if res is not None:
        click.echo("Switched to cluster '{}'".format(cluster_name))
    else:
        click.echo("Can't find cluster '{}'".format(cluster_name))


@cluster.command(help=CLUSTER_LIST_HELP)
@click.pass_obj
def list(obj):
    click.echo("Clusters:")
    clusters = obj.services.config.list_clusters()
    for cluster in clusters:
        click.echo(cluster)


@cluster.command(help=CLUSTER_ADD_HELP)
@click.option('--name',
              required=True)
@click.option('--server',
              required=True)
@click.pass_obj
def add(obj, name, server):
    res = obj.services.config.add_cluster(name, server)
    if res is not None:
        click.echo("Cluster '{}' @ {} added successfully".format(name, server))
    else:
        click.echo("There is already a cluster named '{}'".format(name))


@cluster.command(help=CLUSTER_RM_HELP)
@click.argument("cluster_name")
@click.pass_obj
def rm(obj, cluster_name):
    res = obj.services.config.remove_cluster(cluster_name)
    if res is not None:
        click.echo("Cluster '{}' removed successfully".format(cluster_name))
    else:
        click.echo("There is no '{}' cluster".format(cluster_name))
