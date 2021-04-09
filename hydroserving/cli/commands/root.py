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
from hydroserving.cli.context import CONTEXT_SETTINGS
from hydroserving.core.model.parser import parse_model, parse_metrics
from hydroserving.util.fileutil import get_yamls
from hydroserving.util.yamlutil import yaml_file


@hs_cli.command(
    context_settings=CONTEXT_SETTINGS)
@click.option(
    '--name',
    required=False,
    help="Override name.")
@click.option(
    '--runtime',
    default=None,
    required=False,
    help="Override runtime.")
@click.option(
    '--training-data',
    default=None,
    required=False,
    help="Override training data path.")
@click.option(
    '--install-command',
    default=None,
    required=False,
    help="Override install command.")
@click.option(
    '--dir',
    'target_dir',
    type=click.Path(
        exists=True,
        file_okay=False,
        dir_okay=True),
    default=os.getcwd(),
    show_default=True,
    required=False,
    help="Specify target dir for the model.")
@click.option(
    '--ignore-training-data',
    type=bool,
    required=False,
    default=False,
    is_flag=True,
    help="Flag to omit upload of training data.")
@click.option(
    '--ignore-metrics',
    type=bool,
    required=False,
    default=False,
    is_flag=True,
    help="Flag to omit metrics registration.")
@click.option(
    '--async', 
    'is_async',
    is_flag=True,
    default=False,
    help="Upload the model asynchronously.")
@click.option(
    '-t', '--timeout',
    type=int,
    required=False,
    default=120,
    help="Default timeout for model build process.")
@click.pass_obj
def upload(
        obj: ContextObject, name: str, runtime: str, target_dir: str, training_data: str, 
        ignore_training_data: bool, ignore_metrics: bool, is_async: bool, timeout: int,
        install_command: str, 
):
    """
    Upload a model version to the cluster.
    """
    logging.debug(f"Checking for serving.yaml file in {target_dir}")
    target_dir = os.path.abspath(target_dir)
    serving_files = [
        file for file in get_yamls(target_dir)
        if os.path.splitext(os.path.basename(file))[0] == "serving"
    ]
    logging.debug(f"Found candidates: {serving_files}")
    logging.debug("Taking first for processing")

    serving_file = serving_files[0] if serving_files else None
    if serving_file:
        with open(serving_file, 'r') as f:
            logging.debug(f"Reading {serving_file}")
            resource = yaml_file(f)
        if resource.get('kind') is None:
            logging.error(f"Resource, defined in {serving_file} doesn't specify `kind` field")
            raise SystemExit(1)
        if resource.get('kind') != 'Model':
            logging.error(f"Resource, defined in {serving_file} is not of kind=Model")
            raise SystemExit(1)
        if name is not None:
            logging.debug(f"Replacing name to {name}")
            resource['name'] = name
        if runtime is not None:
            logging.debug(f"Replacing runtime to {runtime}")
            resource['runtime'] = runtime
        if training_data is not None:
            logging.debug(f"Replacing training-data to {training_data}")
            resource['training-data'] = training_data
        if install_command is not None:
            logging.debug(f"Replacing install-command to {install_command}")
            resource['install-command'] = install_command
    else:
        logging.error("Couldn't find serving.yaml for processing")
        raise SystemExit(1)
    
    model_version = obj.model_service.apply(
        parse_model(resource), 
        parse_metrics(resource),
        target_dir,
        ignore_training_data, ignore_metrics, is_async, timeout,
    )
    
    logging.info("Success:")
    logging.info(json.dumps(model_version.to_dict()))


@hs_cli.command(
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
    required=True,
    help="File/dir/stdin to read resources from.")
@click.option(
    '-r', '--recursive',
    type=bool,
    default=False,
    is_flag=True,
    help="Apply recursive search if -f is a directory."
)
@click.option(
    '--ignore-metrics',
    type=bool,
    required=False,
    default=False,
    is_flag=True,
    help="Flag to omit metrics registration.")
@click.option(
    '--ignore-training-data',
    type=bool,
    required=False,
    default=False,
    is_flag=True,
    help="Flag to omit upload of training data.")
@click.pass_obj
def apply(obj: ContextObject, f: str, recursive: bool, ignore_metrics: bool, ignore_training_data: bool):
    """
    Create multiple resources on the cluster.
    """
    fs = list(f)
    for i, x in enumerate(fs):
        if x == "-":
            fs[i] = "<STDIN>"
    logging.debug("Got paths: {}".format(fs))
    try:
        results = obj.apply_service.apply(
            fs, 
            recursive,
            ignore_metrics=ignore_metrics, 
            ignore_training_data=ignore_training_data
        )
        serialized = {
            key : [value.to_dict() for value in values]
            for key, values in results.items()
        }
        logging.info(f"Applied {len(serialized)} resource{'s'[:len(serialized)^1]}:")
        logging.info(json.dumps(serialized))
    except ParserError as ex:
        logging.error("Error while parsing: {}".format(ex))
        raise SystemExit(1)
    except ScannerError as ex:
        logging.error("Error while applying: Invalid YAML: {}".format(ex))
        raise SystemExit(1)
    except Exception as err:
        logging.error("Error while applying: {}".format(err))
        raise SystemExit(1)
