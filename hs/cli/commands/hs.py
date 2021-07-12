import logging

import click
import click_log

from hs.util.logutils import StdoutLogHandler
from hs.cli.context import CONTEXT_SETTINGS
from hs.settings import CONFIG_PATH


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(message="%(prog)s version %(version)s")
@click.option("--verbose", "-v", "verbose",
              default=False,
              is_flag=True,
              help="Enable debug output")
@click.option('--cluster',
              type=click.STRING,
              help="Override the current-cluster option from config",
              required=False)
@click.option('--config-file',
              type=click.Path(exists=True, readable=True, writable=True),
              help=f"Override the default config file at {CONFIG_PATH}",
              show_default=CONFIG_PATH,
              required=False)
@click.pass_context
def hs_cli(ctx, verbose, cluster, config_file):
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
    if config_file:
        ctx.obj = config_file
    else:
        # note: didn't set as default in click, 
        # since CONFIG_FILE is a special case and can be missing
        # and created later using `hs cluster add` command
        ctx.obj = CONFIG_PATH
    logging.debug(f"Working with {ctx.obj} config file")