from tabulate import tabulate
import click

from hs.cli.commands.hs import hs_cli
from hs.cli.help import CLUSTER_HELP, CLUSTER_USE_HELP, CLUSTER_LIST_HELP, CLUSTER_ADD_HELP, \
    CLUSTER_RM_HELP
from hs.entities.cluster_config import ClusterConfig, ClusterDef, ClusterServerDef, \
     read_cluster_config, read_current_cluster, write_cluster_config
from hs.settings import CONFIG_PATH

@hs_cli.group(
    invoke_without_command=True,
    help=CLUSTER_HELP
)
@click.pass_context
def cluster(ctx):
    if ctx.invoked_subcommand is None:
        current_cluster = read_current_cluster(ctx.obj)
        click.echo("Current cluster: {}".format(current_cluster))


@cluster.command(help=CLUSTER_USE_HELP)
@click.argument('cluster_name')
@click.pass_obj
def use(obj, cluster_name):
    config = read_cluster_config(obj)
    if config is None:
        raise click.ClickException("Can't set current cluster. No clusters defined.")

    current_cluster = None
    for cl in config.clusters:
        if cl.name == cluster_name:
            current_cluster = cluster_name
            break
    if current_cluster is None:
        raise click.ClickException(f"Can't find {cluster_name} cluster")
    config.current_cluster = current_cluster
    write_cluster_config(obj, config)

@cluster.command(help=CLUSTER_LIST_HELP)
@click.pass_obj
def list(obj):
    config = read_cluster_config(obj)
    click.echo(f"Current cluster: {config.current_cluster}")
    clusters_view = []
    for cluster in config.clusters:
        clusters_view.append({
            'name': cluster.name,
            'server': cluster.cluster.server
        })
    click.echo(tabulate(sorted(clusters_view, key = lambda x: x['name']), headers="keys", tablefmt="github"))


@cluster.command(help=CLUSTER_ADD_HELP)
@click.option('--name', required=True)
@click.option('--server', required=True)
@click.pass_obj
def add(obj, name, server):
    new_cluster = ClusterDef(name=name, cluster=ClusterServerDef(server=server))
    config = read_cluster_config(obj)
    
    if config is None:
        config = ClusterConfig(
            current_cluster=new_cluster.name,
             clusters = [new_cluster]
        )
    else:
        for cl in config.clusters:
            if cl.name == new_cluster.name:
                raise click.ClickException("Can't add the new cluster. There is already one with the same name.")
        config.clusters.append(new_cluster)
    
    # check if current cluster exists
    current_cluster = None
    for cl in config.clusters:
            if cl.name == config.current_cluster:
                current_cluster = cl
    if current_cluster is None:
        current_cluster = config.clusters[0]
        click.echo(f"Couldn't find current cluster. Setting {current_cluster.name} as current.")
        config.current_cluster = current_cluster.name

    write_cluster_config(obj, config)
    click.echo(f"Cluster {new_cluster.name} at {new_cluster.cluster.server} added successfully")


@cluster.command(help=CLUSTER_RM_HELP)
@click.argument("cluster_name")
@click.pass_obj
def rm(obj, cluster_name):
    config = read_cluster_config(obj)

    if config is None:
        raise click.ClickException("Can't delete. No clusters defined.")

    to_delete = None
    for cl in config.clusters:
        if cl.name == cluster_name:
            to_delete = cl
            break
    
    if to_delete is None:
        raise click.ClickException(f"Can't delete. Cluster {cluster_name} is not found.")

    config.clusters.remove(to_delete)
    write_cluster_config(obj, config)
    click.echo("Deleted successfully")

@cluster.command()
def buildinfo():
    pass
#     from tabulate import tabulate
#     res = obj.config_service.get_cluster_info()
#     logging.info("Cluster build information:")
#     logging.debug(res)
#     logging.info(tabulate(res, headers="keys", tablefmt="github"))

