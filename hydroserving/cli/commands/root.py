import json
import os

import click
import requests
from yaml.parser import ParserError
from yaml.scanner import ScannerError
import logging

from hydroserving.cli.commands.hs import hs_cli
from hydroserving.cli.help import CONTEXT_SETTINGS, UPLOAD_HELP, APPLY_HELP, PROFILE_FILENAME_HELP
from hydroserving.core.model.entities import InvalidModelException
from hydroserving.core.model.package import assemble_model, ensure_model
from hydroserving.core.model.upload import upload_model, ModelBuildError


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
                  dir_okay=True),
              default=os.getcwd(),
              show_default=True,
              required=False)
@click.option('--no-training-data',
              type=bool,
              required=False,
              default=False,
              is_flag=True)
@click.option('--ignore-monitoring',
              type=bool,
              required=False,
              default=False,
              is_flag=True)
@click.option('--async', 'is_async', is_flag=True, default=False)
@click.pass_obj
def upload(obj, name, runtime, host_selector, training_data, dir, no_training_data, ignore_monitoring, is_async):
    dir = os.path.abspath(dir)
    try:
        model_metadata = ensure_model(dir, name, runtime, host_selector, training_data)
        logging.info("Assembling model payload")
        tar = assemble_model(model_metadata, dir)
        current_cluster = obj.config_service.current_cluster()
        logging.info("Uploading payload to cluster '{}' at {}".format(
            current_cluster['name'], current_cluster['cluster']['server']))
        result = upload_model(obj.model_service, obj.monitoring_service, model_metadata,
                              tar, is_async, no_training_data, ignore_monitoring)
        logging.info("Success:")
        click.echo(json.dumps(result))
    except ModelBuildError as err:
        logging.error("Model build failed")
        logging.info(json.dumps(err.model_version))
        raise SystemExit(-1)
    except requests.RequestException as err:
        logging.error("Server returned an error")
        logging.info(err)
        raise SystemExit(-1)
    except ValueError as err:
        logging.error("Upload failed")
        logging.info(err)
        raise SystemExit(-1)
    except InvalidModelException as err:
        logging.error("Invalid model definition")
        logging.info(err)
    except RuntimeError as err:
        logging.error("Unexpected error")
        logging.info(err)
        logging.info(err.__traceback__)


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
    f = list(f)
    for i, x in enumerate(f):
        if x == "-":
            f[i] = "<STDIN>"
    logging.debug("Got files: {}".format(f))
    try:
        result = obj.apply_service.apply(f, ignore_monitoring=ignore_monitoring)
        logging.info(json.dumps(result))
    except ParserError as ex:
        logging.error("Error while parsing: {}".format(ex))
        raise SystemExit(-1)
    except ScannerError as ex:
        logging.error("Error while applying: Invalid YAML: {}".format(ex))
        raise SystemExit(-1)
    except Exception as err:
        logging.error("Error while applying: {}".format(err))
        raise SystemExit(-1)
