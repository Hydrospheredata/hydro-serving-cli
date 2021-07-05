import click
from tabulate import tabulate

from hs.cli.commands.hs import hs_cli
from hs.cli.context import CONTEXT_SETTINGS
from hs.cli.help import PROFILE_HELP
from hs.entities.cluster_config import get_cluster_connection
from hydrosdk.modelversion import ModelVersion

@hs_cli.group(help=PROFILE_HELP)
@click.pass_context
def model(ctx):
    ctx.obj = get_cluster_connection()


@model.command(context_settings=CONTEXT_SETTINGS)
@click.pass_obj
def list(obj):
    models = ModelVersion.list(obj)
    versions_view = []
    for m in models:
        versions_view.append({
            'id': m.id,
            'name': m.name,
            '#': m.version,
            'status': m.status,
            'runtime': str(m.runtime),
            'apps': m.applications
        })
    click.echo(tabulate(sorted(versions_view, key=lambda x: (x['name'], x['#'])), headers="keys", tablefmt="github"))


# todo: can't find delete model method in SDK
# @model.command(context_settings=CONTEXT_SETTINGS)
# @click.argument('model-name',
#                 required=True)
# @click.pass_obj
# def rm(obj, model_name):
    
#     mv = obj.model_service.find_model(model_name)
#     if not mv:
#         raise click.ClickException("Model {} not found".format(model_name))
#     mv_id = mv['id']
#     res = obj.model_service.delete(mv_id)
#     logging.info("Model and it's versions are deleted: %s", res)


@model.command(context_settings=CONTEXT_SETTINGS)
@click.argument('model-name', required=True)
@click.pass_obj
def logs(obj, model_name):
    (name, version) = model_name.split(':')
    mv = ModelVersion.find(obj, name, version)
    logs = mv.build_logs()
    for l in logs:
        click.echo(l.data)
    click.echo("End of logs")
