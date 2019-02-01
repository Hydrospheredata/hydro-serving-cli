import os

import click

from hydroserving.cli.context import CONTEXT_SETTINGS
from hydroserving.config.settings import HOME_PATH_EXPANDED
from hydroserving.cli.context_object import ContextObject


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(message="%(prog)s version %(version)s")
@click.pass_context
def hs_cli(ctx):
    if not os.path.isdir(HOME_PATH_EXPANDED):
        os.mkdir(HOME_PATH_EXPANDED)

    ctx.obj = ContextObject.with_config_path(HOME_PATH_EXPANDED)
