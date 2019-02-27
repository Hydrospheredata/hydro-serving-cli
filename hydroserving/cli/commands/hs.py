import os

import click
import click_log
import logging
from hydroserving.cli.context import CONTEXT_SETTINGS
from hydroserving.cli.help import VERBOSE_HELP
from hydroserving.config.settings import HOME_PATH_EXPANDED
from hydroserving.cli.context_object import ContextObject


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
    if verbose:
        logging.root.setLevel(logging.DEBUG)
    else:
        logging.root.setLevel(logging.INFO)

    if not os.path.isdir(HOME_PATH_EXPANDED):
        logging.debug("Didn't find {} folder. Creating...".format(HOME_PATH_EXPANDED))
        os.mkdir(HOME_PATH_EXPANDED)
    try:
        if cluster:
            logging.debug("Overriding current cluster with {}".format(cluster))
            ctx.obj = ContextObject.with_config_path(HOME_PATH_EXPANDED, overridden_cluster=cluster)
        else:
            ctx.obj = ContextObject.with_config_path(HOME_PATH_EXPANDED)
    except Exception as err:
        logging.error("Error occurred while preparing cluster: {}".format(err))
        raise SystemExit(-1)

    logging.debug("Current cluster: {}".format(ctx.obj.config_service.current_cluster()))
