import json
import logging
import os

import click
import requests
from click import ClickException
from yaml.parser import ParserError
from yaml.scanner import ScannerError

from hydroserving.cli.commands.hs import hs_cli
from hydroserving.cli.help import CONTEXT_SETTINGS, UPLOAD_HELP, APPLY_HELP, PROFILE_FILENAME_HELP
from hydroserving.core.image import DockerImage
from hydroserving.core.model.entities import InvalidModelException
from hydroserving.core.model.parser import parse_model
from hydroserving.core.model.upload import ModelBuildError
from hydroserving.util.fileutil import get_yamls, get_python_files
from hydroserving.util.yamlutil import yaml_file


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
        python_files = [
            file 
            for file in get_python_files(dir)
            if os.path.splitext(os.path.basename(file))[0] == "serving"
        ]
        python_file = python_files[0] if python_files else None
        serving_files = [
            file
            for file in get_yamls(dir)
            if os.path.splitext(os.path.basename(file))[0] == "serving"
        ]
        serving_file = serving_files[0] if serving_files else None
        if python_file:
            import sys
            import pathlib
            import importlib
            sys.path.append(dir)
            module_name = pathlib.Path(python_file).stem
            try:
                importlib.import_module(module_name) # runs setup() on import
            except Exception as e:
                logging.error("Error occured while trying to read serving.py", exc_info=e)
                raise click.ClickException("Error occured while trying to read serving.py")
            return 0
        elif serving_file:
            with open(serving_file, 'r') as f:
                parsed = yaml_file(f)
                if parsed.get('kind', 'None') != 'Model':
                    raise ClickException("Resource defined in {} is not a Model".format(serving_file))
                if name is not None:
                    parsed['name'] = name
                if runtime is not None:
                    parsed['runtime'] = runtime
                if host_selector is not None:
                    parsed['host_selector'] = host_selector
                if training_data is not None:
                    parsed['training_data_file'] = training_data
        else:
            logging.info("Not using any resource definitions. Will try to infer metadata from current folder.")
            if name is None:
                name = os.path.basename(os.getcwd())
            parsed = {
                'name': name,
                'runtime': runtime,
                'host_selector': host_selector,
                'payload': [os.path.join(dir, "*")],
                'training_data_file': training_data,
            }
        model = parse_model(parsed)
        result = obj.model_service.apply(model, dir, no_training_data, ignore_monitoring)
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
