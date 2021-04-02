import logging
import traceback

import click
import click_log
from click import Context

from hydroserving.cli.context import CONTEXT_SETTINGS
from hydroserving.cli.context_object import ContextObject
from hydroserving.cli.help import VERBOSE_HELP
from hydroserving.util.log_handler import StdoutLogHandler, PrettyFormatter
from hydroserving.errors.config import ClusterNotFoundError


@click.group(
    context_settings=CONTEXT_SETTINGS)
@click.option(
    "-v", "--verbose",
    default=False,
    is_flag=True,
    help="Enable debug output.")
@click.option(
    "-p", "--pretty-print",
    default=False,
    is_flag=True,
    help="Format JSON outputs with indents.")
@click.option(
    "-c", "--cluster",
    required=False,
    help="Use a given cluster during a command execution.")
@click.version_option(
    message="%(prog)s version %(version)s")
@click.pass_context
def hs_cli(ctx: Context, verbose: bool, cluster: str, pretty_print: bool):
    click_log.basic_config(logging.root)
    log_handler = StdoutLogHandler()
    log_handler.formatter = PrettyFormatter(pretty_print)
    logging.root.handlers = [log_handler]
    if verbose:
        logging.root.setLevel(logging.DEBUG)
    else:
        logging.root.setLevel(logging.INFO)

    if cluster:
        logging.debug("Overriding current cluster with {}".format(cluster))
        ctx.obj = ContextObject.with_config_path(overridden_cluster=cluster)
    else:
        ctx.obj = ContextObject.with_config_path()

    try: 
        logging.debug("Current cluster: {}".format(ctx.obj.config_service.current_cluster()))
    except ClusterNotFoundError:
        pass
