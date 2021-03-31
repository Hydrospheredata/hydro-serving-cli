import logging
import json

import click
from click_aliases import ClickAliasedGroup
from tabulate import tabulate

from hydroserving.cli.commands.hs import hs_cli
from hydroserving.cli.context_object import ContextObject
from hydroserving.errors.config import ClusterNotFoundError, ClusterAlreadyExistsError


@hs_cli.group(
    cls=ClickAliasedGroup,
    invoke_without_command=True,
)
@click.pass_context
def cluster(ctx):
    """
    Manage Hydrosphere clusters.
    """
    if ctx.invoked_subcommand is None:
        try: 
            cluster = ctx.obj.config_service.current_cluster()
            logging.info("Current cluster: {}".format(cluster))
        except ClusterNotFoundError:
            logging.error("Current cluster is unset, use 'hs cluster set [NAME]' to set an active cluster")


@cluster.command(
    aliases=["use"])
@click.argument('name')
@click.pass_obj
def set(obj: ContextObject, name: str):
    """
    Set active cluster to the given one.
    """
    try:
        res = obj.config_service.select_cluster(name)
        logging.info("Switched to cluster '{}'".format(res))
    except ClusterNotFoundError as e:
        logging.error(f"Couldn't find '{name}' cluster")
        raise SystemExit(1)


@cluster.command(
    aliases=["ls"])
@click.pass_obj
def list(obj: ContextObject):
    """
    List available clusters. 
    """
    view = []
    try:
        current_cluster = obj.config_service.current_cluster()['name']
    except (ClusterNotFoundError, KeyError):
        current_cluster = None
    for cluster in obj.config_service.list_clusters():
        name = cluster.get("name", "unknown")
        view.append({
            "active": "*" if current_cluster == name else "",
            "name": name,
            "server": cluster.get("cluster", {}).get("server", "unknown")
        })
    if view:
        logging.info(tabulate(view, headers="keys", tablefmt="github"))
    else:
        logging.info("Couldn't find any clusters")


@cluster.command()
@click.option('--name', required=True)
@click.option('--server', required=True)
@click.pass_obj
def add(obj: ContextObject, name: str, server: str):
    """
    Register a new cluster.
    """
    try:
        res = obj.config_service.add_cluster(name, server)
        if res is not None:
            logging.info("Cluster '{}' @ {} added successfully".format(name, server))
        else:
            logging.error("There is already a cluster named '{}'".format(name))
            raise SystemExit(1)
    except ValueError as err:
        logging.error("Cluster validation error: {}".format(err))
        raise SystemExit(1)
    except ClusterAlreadyExistsError as e:
        logging.error(f"Cluster '{name}' already exists")
        raise SystemExit(1)

@cluster.command(
    aliases=["del", "remove", "rm"])
@click.argument("name")
@click.pass_obj
def delete(obj: ContextObject, name: str):
    """
    Delete a cluster.
    """
    try: 
        obj.config_service.remove_cluster(name)
        logging.info("Cluster '{}' removed successfully".format(name))
    except ClusterNotFoundError:
        logging.error(f"Cluster '{name}' not found")


@cluster.command()
@click.option(
    '-s', '--ignore-errors', 
    'is_silent',
    type=bool,
    is_flag=True,
    default=False,
    help="Omit warning and error messages from the output")
@click.pass_obj
def buildinfo(obj: ContextObject, is_silent: bool):
    """
    Retrieve buildinfo from the active cluster.
    """
    response = obj.config_service.get_cluster_buildinfo(is_silent)
    if not response:
        logging.error("Couldn't retrieve any buildinfo")
    else: 
        logging.info(json.dumps(response))
