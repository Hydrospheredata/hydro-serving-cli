import os

import click

from hydroserving.constants.click import CONTEXT_SETTINGS
from hydroserving.constants.config import HOME_PATH_EXPANDED
from hydroserving.models.context_object import ContextObject, ContextServices


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(message="%(prog)s version %(version)s")
@click.pass_context
def hs_cli(ctx):
    if not os.path.isdir(HOME_PATH_EXPANDED):
        os.mkdir(HOME_PATH_EXPANDED)
    ctx.obj = ContextObject()

    ctx.obj.services = ContextServices.with_config_path(HOME_PATH_EXPANDED)
