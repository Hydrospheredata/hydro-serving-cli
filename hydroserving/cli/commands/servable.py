import click
import logging

from tabulate import tabulate

from hydroserving.cli.commands.hs import hs_cli
from hydroserving.cli.context import CONTEXT_SETTINGS
from hydroserving.cli.help import PROFILE_HELP, PROFILE_PUSH_HELP, PROFILE_MODEL_VERSION_HELP


@hs_cli.group(help=PROFILE_HELP)
def servable():
    pass


@servable.command(context_settings=CONTEXT_SETTINGS)
@click.pass_obj
def list(obj):
    servables = obj.servable_service.list()
    if servables:
        servables_view = []
        for m in servables:
            servable_name = m.get('fullName')
            version = m.get('modelVersion')
            model = version.get('model')
            if not servable_name:
                suffix = m.get('nameSuffix')
                servable_name = "{}-{}-{}".format(model.get('name'), version.get('modelVersion'), suffix).replace('_', '-')
            status_obj = m.get('status')
            status = status_obj.get('status')
            status_msg = status_obj.get('msg')
            servables_view.append({
                'name': servable_name,
                'status': status,
                'message': status_msg,
            })
        logging.info(tabulate(sorted(servables_view, key = lambda x: x['name']), headers="keys", tablefmt="github"))
    else:
        logging.warning("Can't get servables list: %s", servables)
        raise SystemExit(-1)

@servable.command(context_settings=CONTEXT_SETTINGS)
@click.argument('model-name', required=True)
@click.pass_obj
def deploy(obj, model_name):
    (name, version) = model_name.split(':')
    version = int(version)
    mv = obj.model_service.find_version(name, version)
    if not mv:
        raise click.ClickException("Model {} not found".format(model_name))
    try:
        res = obj.servable_service.create(name, version)
    except Exception as e:
        raise click.ClickException("Can't deploy servable because there are internal errors: {}".format(e))
    logging.info(res)

@servable.command(context_settings=CONTEXT_SETTINGS)
@click.argument('servable-name',
                required=True)
@click.pass_obj
def rm(obj, servable_name):
    s = obj.servable_service.get(servable_name)
    if s:
        deleted = obj.servable_service.delete(servable_name)
        if deleted:
            logging.info("Servable {} was deleted".format(servable_name))
        else:
            logging.error("Servable {} wasn't deleted".format(servable_name))
            raise SystemExit(-1)
    else:
        logging.error("Servable {} doesn't exist".format(servable_name))
        raise SystemExit(-1)


@servable.command(context_settings=CONTEXT_SETTINGS)
@click.argument('servable-name', required=True)
@click.option('--follow', '-f', required=False, default=False, type=bool, is_flag=True)
@click.pass_obj
def logs(obj, servable_name, follow):
    iterator = obj.servable_service.logs(servable_name, follow)
    if iterator:
        for event in iterator:
            if event:
                logging.info(event.data)
    else:
        logging.error("Cannot fetch logs for %s", (servable_name,))
        raise SystemExit(-1)
