import click
from hydroserving.cli.hs import hs_cli

@hs_cli.group()
@click.pass_context
def dev(ctx):
    pass
