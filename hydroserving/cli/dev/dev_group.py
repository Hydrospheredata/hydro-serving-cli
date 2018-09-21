import click
from hydroserving.cli.hs import hs_cli
from hydroserving.constants.help import DEV_HELP


@hs_cli.group(help=DEV_HELP)
@click.pass_context
def dev(ctx):
    pass
