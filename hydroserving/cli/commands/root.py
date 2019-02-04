import os
import pprint
import json
import sys

import click
import requests
from yaml.scanner import ScannerError

from hydroserving.cli.commands.hs import hs_cli
from hydroserving.cli.help import CONTEXT_SETTINGS, UPLOAD_HELP, APPLY_HELP, PROFILE_FILENAME_HELP
from hydroserving.cli.upload import upload_model
from hydroserving.cli.utils import ensure_model
from hydroserving.core.apply import ApplyError
from hydroserving.core.model.package import assemble_model
from hydroserving.core.parsers.abstract import ParserError


@hs_cli.command(help=UPLOAD_HELP, context_settings=CONTEXT_SETTINGS)
@click.option('--name',
              required=False)
@click.option('--runtime',
              default=None,
              required=False)
@click.option('--host-selector',
              default=None,
              required=False)
@click.option('--training-data',
              type=click.File(),
              default=None,
              required=False,
              help=PROFILE_FILENAME_HELP)
@click.option('--dir',
              type=click.Path(
                  exists=True,
                  file_okay=False,
                  dir_okay=True
              ),
              default=os.getcwd(),
              show_default=True,
              required=False)
@click.option('--async', 'is_async', is_flag=True, default=False)
@click.pass_obj
def upload(obj, name, runtime, host_selector, training_data, dir, is_async):
    cluster = obj.config_service.current_cluster()
    if cluster is None:
        click.echo("No cluster selected. Cannot continue.")
        raise SystemExit(-1)

    click.echo("Using '{}' cluster".format(cluster['name']))

    model_metadata = ensure_model(dir, name, runtime, host_selector, training_data)

    try:
        tar = assemble_model(model_metadata, dir)
        result = upload_model(obj.model_service, obj.profiler_service, model_metadata, tar, is_async)
        click.echo("Success:")
        click.echo(json.dumps(result))
    except requests.RequestException as err:
        click.echo()
        click.echo("Upload failed. Reason:")
        click.echo(err)
        raise SystemExit(-1)
    except ValueError as err:
        click.echo("Upload failed: {}".format(err))
        raise SystemExit(-1)


@hs_cli.command(help=APPLY_HELP, context_settings=CONTEXT_SETTINGS)
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
@click.option('--ignore-monitoring',
              type=bool,
              required=False,
              default=False,
              is_flag=True)
@click.pass_obj
def apply(obj, f, ignore_monitoring):
    try:
        result = obj.apply_service.apply(f, ignore_monitoring=ignore_monitoring)
        click.echo(json.dumps(result))
    except ApplyError as ex:
        click.echo("Error while applying {}".format(f))
        click.echo(ex)
        raise SystemExit(-1)
    except ParserError as ex:
        click.echo("Error while applying: {}".format(f))
        click.echo(ex)
        raise SystemExit(-1)
    except ScannerError as ex:
        click.echo("Error while applying: {}".format(f))
        click.echo("Invalid YAML format: {}".format(ex))