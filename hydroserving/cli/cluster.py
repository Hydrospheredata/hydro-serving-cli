import click

from hydroserving.cli.hs import hs_cli


@hs_cli.group(invoke_without_command=True)
@click.pass_context
def cluster(ctx):
    if ctx.invoked_subcommand is None:
        click.echo("Current cluster: {}".format(ctx.obj.services.config.current_cluster()))


@cluster.command()
@click.argument('cluster_name')
@click.pass_obj
def use(obj, cluster_name):
    res = obj.services.config.select_cluster(cluster_name)
    if res is not None:
        click.echo("Switched to cluster '{}'".format(cluster_name))
    else:
        click.echo("Can't find cluster '{}'".format(cluster_name))


@cluster.command()
@click.pass_obj
def list(obj):
    click.echo("Clusters:")
    clusters = obj.services.config.list_clusters()
    for cluster in clusters:
        click.echo(cluster)


@cluster.command()
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


@cluster.command()
@click.argument("cluster_name")
@click.pass_obj
def rm(obj, cluster_name):
    res = obj.services.config.remove_cluster(cluster_name)
    if res is not None:
        click.echo("Cluster '{}' removed successfully".format(cluster_name))
    else:
        click.echo("There is no '{}' cluster".format(cluster_name))
