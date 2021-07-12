import yaml
from yaml.error import MarkedYAMLError, YAMLError
from hs.entities.deployment_config import DeploymentConfig
from hs.entities.application import Application
import os
import sys
import logging

import click
from yaml.parser import ParserError
from yaml.scanner import ScannerError

from hs.cli.commands.hs import hs_cli
from hs.cli.context import CONTEXT_SETTINGS
from hs.entities.cluster_config import get_cluster_connection
from hs.entities.model_version import ModelVersion


@hs_cli.command(
    help="Applies YAML definition files and creates resources on Hydrosphere serving cluster",
    context_settings=CONTEXT_SETTINGS)
@click.option('-f',
              type=click.Path(
                  exists=True,
                  file_okay=True,
                  dir_okay=True,
                  allow_dash=True,
                  readable=True
              ),
              multiple=True,
              required=True)
@click.pass_obj
def apply(obj, f):
    conn = get_cluster_connection(obj)
    for path in f:
        if path == "-":
            content = list(yaml.safe_load_all(sys.stdin))
            cwd = os.getcwd()
        else:
            with open(path, "r") as f:
                content = list(yaml.safe_load_all(f))
                cwd = os.path.dirname(path)
        for doc in content:
            parse_apply(path, conn, cwd, doc)



def parse_apply(arg, conn, cwd, raw_dict):
    kind = raw_dict.get('kind')
    if not kind:
        raise click.ClickException(f"No 'kind' field specified in {arg}.")
    if kind == "Model":
        mv_def = ModelVersion.parse_obj(raw_dict)
        click.echo("Applying the following model version:")
        click.echo(mv_def.to_yaml())
        result = mv_def.apply(conn, cwd)
        click.echo(f"Model {result.name}:{result.version} was applied successfully")
    elif kind == "Application":
        app_def = Application.parse_obj(raw_dict)
        click.echo("Applying the following application:")
        click.echo(app_def.to_yaml())
        result = app_def.apply(conn, cwd)
        click.echo(f"Application {result.name} with id {result.id} was applied successfully")
    elif kind == "DeploymentConfiguration":
        dc_def = DeploymentConfig.parse_obj(raw_dict)
        click.echo("Applying the following deployment configuration:")
        click.echo(dc_def.to_yaml())
        result = dc_def.apply(conn)
        click.echo(f"Deployment configuration {result.name} was applied successfully")
    else:
        raise click.ClickException(f"Kind {kind} in {arg} is not supported")