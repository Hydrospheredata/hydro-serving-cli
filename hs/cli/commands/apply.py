import os
from hs.entities.model_version import ModelVersion
from hs.util.yamlutil import yaml_file, yaml_file_stream
import sys
import logging

import click
from yaml.parser import ParserError
from yaml.scanner import ScannerError

from hs.cli.commands.hs import hs_cli
from hs.cli.context import CONTEXT_SETTINGS
from hs.entities.cluster_config import get_cluster_connection


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
        try:
            if path == "-":
                content = yaml_file_stream(sys.stdin)
                cwd = os.getcwd()
            else:
                with open(path, "r") as f:
                    content = yaml_file_stream(f)
                    cwd = os.path.dirname(path)
            for doc in content:
                parse_apply(path, conn, cwd, doc)
        except ParserError as ex:
            logging.exception("Error while parsing: {}".format(ex))
            raise SystemExit(-1)
        except ScannerError as ex:
            logging.exception("Error while applying: Invalid YAML: {}".format(ex))
            raise SystemExit(-1)
        except Exception as err:
            logging.exception("Error while applying: {}".format(err))
            raise SystemExit(-1)

KIND_MAPPING = {
    "Model": ModelVersion.parse_obj,
    # "Application": Application.parse_obj,
    # "DeploymentConfig": DeploymentConfig.parse_obj,
    # "Servable": Servable.parse_obj,
}

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
    else:
        raise click.ClickException(f"Kind {kind} in {arg} is not supported")