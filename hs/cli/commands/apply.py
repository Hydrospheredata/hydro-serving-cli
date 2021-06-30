import json
import logging

import click
from yaml.parser import ParserError
from yaml.scanner import ScannerError

from hs.cli.commands.hs import hs_cli
from hs.cli.help import APPLY_HELP
from hs.cli.context import CONTEXT_SETTINGS


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
