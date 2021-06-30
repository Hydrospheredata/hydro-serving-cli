import logging

import click
import click_log

from hs.cli.help import VERBOSE_HELP
from hs.util.log_handler import StdoutLogHandler
from hs.cli.context import CONTEXT_SETTINGS


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(message="%(prog)s version %(version)s")
@click.option("--verbose", "-v", "verbose",
              default=False,
              is_flag=True,
              help=VERBOSE_HELP)
@click.option('--cluster',
              type=click.STRING,
              required=False)
@click.pass_context
def hs_cli(ctx, verbose, cluster):
    click_log.basic_config(logging.root)
    # custom handler to print output into stdout
    log_handler = StdoutLogHandler()
    log_handler.formatter = click_log.ColorFormatter()
    logging.root.handlers = [log_handler]
    if verbose:
        logging.root.setLevel(logging.DEBUG)
    else:
        logging.root.setLevel(logging.INFO)
    logging.debug("CLI root command (hs_cli) initialized")
