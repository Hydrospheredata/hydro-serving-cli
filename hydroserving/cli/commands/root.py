import json
import logging
import os

import click
import requests
from click import ClickException
from yaml.parser import ParserError
from yaml.scanner import ScannerError

from hydroserving.cli.context_object import ContextObject
from hydroserving.cli.commands.hs import hs_cli
from hydroserving.cli.help import (
    CONTEXT_SETTINGS, UPLOAD_HELP, APPLY_HELP, PROFILE_FILENAME_HELP,
)
from hydroserving.core.model.parser import parse_model
from hydroserving.util.fileutil import get_yamls
from hydroserving.util.yamlutil import yaml_file


@hs_cli.command(
    help=UPLOAD_HELP, 
    context_settings=CONTEXT_SETTINGS)
@click.option(
    '--name',
    required=False)
@click.option(
    '--runtime',
    default=None,
    required=False)
@click.option(
    '--training-data',
    default=None,
    required=False,
    help=PROFILE_FILENAME_HELP)
@click.option(
    '--dir',
    'target_dir',
    type=click.Path(
        exists=True,
        file_okay=False,
        dir_okay=True),
    default=os.getcwd(),
    show_default=True,
    required=False)
@click.option(
    '--ignore-training-data',
    type=bool,
    required=False,
    default=False,
    is_flag=True)
@click.option(
    '--ignore-metrics',
    type=bool,
    required=False,
    default=False,
    is_flag=True)
@click.option(
    '--async', 
    'is_async',
    is_flag=True,
    default=False)
@click.option(
    '-t', '--timeout',
    type=int,
    required=False,
    default=120)
@click.pass_obj
def upload(
        obj: ContextObject, name: str, runtime: str, target_dir: str, training_data: str, 
        ignore_training_data: bool, ignore_metrics: bool, is_async: bool, timeout: int,
):
    target_dir = os.path.abspath(target_dir)
    serving_files = [
        file for file in get_yamls(target_dir)
        if os.path.splitext(os.path.basename(file))[0] == "serving"
    ]
    serving_file = serving_files[0] if serving_files else None

    if serving_file:
        with open(serving_file, 'r') as f:
            parsed = yaml_file(f)
        if parsed.get('kind', 'None') != 'Model':
            raise ClickException(f"Resource defined in {serving_file} is not a Model")
        if name is not None:
            parsed['name'] = name
        if runtime is not None:
            parsed['runtime'] = runtime
        if training_data is not None:
            parsed['training-data'] = training_data
    else:
        raise ClickException("Couldn't find any resource definitions(serving.yaml).")
    
    model_version = obj.model_service.apply(
        parse_model(parsed), target_dir,
        ignore_training_data, ignore_metrics, is_async, timeout,
    )
    
    logging.info("Success:")
    click.echo(json.dumps(model_version.to_dict()))


@hs_cli.command(
    help=APPLY_HELP, 
    context_settings=CONTEXT_SETTINGS)
@click.option(
    '-f',
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=True,
        allow_dash=True,
        readable=True),
    multiple=True,
    required=True)
@click.option(
    '--ignore-metrics',
    type=bool,
    required=False,
    default=False,
    is_flag=True)
@click.option(
    '--ignore-training-data',
    type=bool,
    required=False,
    default=False,
    is_flag=True)
@click.pass_obj
def apply(obj: ContextObject, f: str, ignore_metrics: bool, ignore_training_data: bool):
    f = list(f)
    for i, x in enumerate(f):
        if x == "-":
            f[i] = "<STDIN>"
    logging.debug("Got files: {}".format(f))
    try:
        results = obj.apply_service.apply(
            f, 
            ignore_metrics=ignore_metrics, 
            ignore_training_data=ignore_training_data
        )
        serialized = {
            key : [value.to_dict() for value in values]
            for key, values in results.items()
        }
        logging.info(json.dumps(serialized))
    except ParserError as ex:
        logging.error("Error while parsing: {}".format(ex))
        raise SystemExit(-1)
    except ScannerError as ex:
        logging.error("Error while applying: Invalid YAML: {}".format(ex))
        raise SystemExit(-1)
    except Exception as err:
        logging.error("Error while applying: {}".format(err))
        raise SystemExit(-1)
