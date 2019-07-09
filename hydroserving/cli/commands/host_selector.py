import click
import logging
import itertools

from tabulate import tabulate

from hydroserving.cli.commands.hs import hs_cli
from hydroserving.cli.context import CONTEXT_SETTINGS
from hydroserving.cli.help import HOST_SELECTOR_HELP, HOST_SELECTOR_LIST_HELP, HOST_SELECTOR_ADD_HELP, HOST_SELECTOR_RM_HELP, HOST_SELECTOR_NODE_SELECTOR_HELP


@hs_cli.group(help=HOST_SELECTOR_HELP)
def host_selector():
  pass


@host_selector.command(context_settings=CONTEXT_SETTINGS, help=HOST_SELECTOR_LIST_HELP)
@click.pass_obj
def list(obj):
  selectors = obj.selector_service.list()
  if selectors:
    selector_view = []
    for s in selectors:
      name = s.get('name')
      node_selectors = s.get('nodeSelector')
      first_selector = [(k,v) for k,v in node_selectors.items()][0]
      selector_view.append({
        "name": name,
        "key": first_selector[0],
        "value": first_selector[1]
      })
      for key, value in itertools.islice(node_selectors.items(), 1, len(node_selectors)):
        selector_view.append({
          "name": "",
          "key": key,
          "value": value
        })
    logging.info(tabulate(selector_view, headers="keys", tablefmt="github"))
  else:
    logging.warning("Can't get host selector list: %s", selectors)
    raise SystemExit(-1)

@host_selector.command(context_settings=CONTEXT_SETTINGS, help=HOST_SELECTOR_ADD_HELP)
@click.argument('name', required=True)
@click.option('--node-selector', '-ns', default=None, required=True, help=HOST_SELECTOR_NODE_SELECTOR_HELP, multiple=True)
@click.pass_obj
def create(obj, name, node_selector):
  node_selector_dict = dict([tuple(x.split(":")) for x in node_selector])
  res = obj.selector_service.create(name, node_selector_dict)
  logging.info("Host Selector was created: %s" % (res, ))
  # print("Creating %s, node selectors: %s" % (name, str(node_selector_dict)))

@host_selector.command(context_settings=CONTEXT_SETTINGS, help=HOST_SELECTOR_RM_HELP)
@click.argument('host-selector-name',
                required=True)
@click.pass_obj
def rm(obj, host_selector_name):
  selector = obj.selector_service.get(host_selector_name)
  if not selector:
    raise click.ClickException("Host Selector {} not found".format(host_selector_name))
  res = obj.selector_service.delete(host_selector_name)
  logging.info("Host Selector %s was deleted", host_selector_name)
