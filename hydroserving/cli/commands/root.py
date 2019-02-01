import os
import pprint
import json
import click
import requests

from hydroserving.cli.commands.hs import hs_cli
from hydroserving.cli.help import CONTEXT_SETTINGS, UPLOAD_HELP, APPLY_HELP, PROFILE_FILENAME_HELP
from hydroserving.cli.upload import upload_model
from hydroserving.cli.utils import ensure_model
from hydroserving.config.settings import TARGET_FOLDER
from hydroserving.core.apply import ApplyError
from hydroserving.core.model.package import assemble_model
from hydroserving.core.parsers.abstract import ParserError


@hs_cli.command(help=UPLOAD_HELP, context_settings=CONTEXT_SETTINGS)
@click.option('--name',
              default=os.path.basename(os.getcwd()),
              show_default=True,
              required=False)
@click.option('--model_type',
              default=None,
              required=False)
@click.option('--contract',
              type=click.Path(exists=True),
              default=None,
              required=False)
@click.option('--training-data',
              type=click.Path(exists=True),
              default=None,
              required=False,
              help=PROFILE_FILENAME_HELP)
@click.option('--description',
              default=None,
              required=False)
@click.option('--async', 'is_async', is_flag=True, default=False)
@click.pass_obj
def upload(obj, name, model_type, contract, training_data, description, is_async):
    cluster = obj.config_service.current_cluster()
    if cluster is None:
        click.echo("No cluster selected. Cannot continue.")
        raise SystemExit(-1)

    click.echo("Using '{}' cluster".format(cluster['name']))

    model_metadata = ensure_model(os.getcwd(), name, model_type, description, contract, training_data)

    try:
        tar = assemble_model(model_metadata, TARGET_FOLDER)
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
              type=click.Path(exists=True),
              multiple=True,
              required=True)
@click.option('--ignore-monitoring',
              type=bool,
              required=False,
              default=False,
              is_flag=True)
@click.pass_obj
def apply(obj, f, ignore_monitoring):
    apply_service = obj.apply_service
    try:
        result = apply_service.apply(f, ignore_monitoring=ignore_monitoring)
        click.echo(pprint.pformat(result))
    except ApplyError as ex:
        click.echo("Error while applying {}".format(f))
        click.echo(ex)
        raise SystemExit(-1)
    except ParserError as ex:
        click.echo("Error while applying: {}".format(f))
        click.echo(ex)
        raise SystemExit(-1)