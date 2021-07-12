import click
from hydrosdk.modelversion import ModelVersion, _upload_local_file, _upload_s3_file, _upload_training_data

from hs.cli.commands.hs import hs_cli
from hs.cli.context import CONTEXT_SETTINGS
from hs.cli.help import PROFILE_HELP, PROFILE_PUSH_HELP, PROFILE_MODEL_VERSION_HELP
from hs.entities.cluster_config import get_cluster_connection


@hs_cli.group(help=PROFILE_HELP)
@click.pass_context
def profile(ctx):
    ctx.obj = get_cluster_connection()


@profile.command(help=PROFILE_PUSH_HELP, context_settings=CONTEXT_SETTINGS)
@click.option('--model-version',
              required=True,
              help=PROFILE_MODEL_VERSION_HELP)
@click.option('--filename',
              type=click.File(mode='rb'),
              required=False
              )
@click.option('--s3path',
              type=click.STRING,
              required=False)
@click.option('--async', 'is_async', is_flag=True, default=False)
@click.pass_obj
def push(obj, model_version, filename, s3path):
    model, version = model_version.split(":")
    mv = ModelVersion.find(obj, model, int(version))
    if filename and s3path:
        raise click.ClickException("Both --filename and --s3path were provided. Need only one of them.")
    if filename:
        click.echo("Uploading local file")
        res = _upload_local_file(obj, mv.id, filename)
        if res.ok:
            click.echo("Data uploaded")
        else:
            raise click.ClickException(str(res))
    elif s3path:
        click.echo("Uploading S3 path")
        res = _upload_s3_file(obj, mv.id, s3path)
        if res.ok:
            click.echo("Data uploaded")
        else:
            raise click.ClickException(str(res))
    else:
        raise click.ClickException("Neither S3 nor file was defined.")
    click.echo(f"Data profile for {model_version} will be available: {obj.http_address}/models/{mv.name}/{mv.version}")


# todo: not supported by SDK (GET /monitoring/profiles/batch/{model_version_id}/status)
# @profile.command(context_settings=CONTEXT_SETTINGS)
# @click.argument('model-version',
#                 required=True)
# @click.pass_obj
# def status(obj, model_version):
#     model, version = model_version.split(":")
#     mv = ModelVersion.find(obj, model, int(version))
#     res = obj.monitoring_service.get_data_processing_status(mv_id)
#     logging.info("Looking for profiling status for model id=%s name=%s version=%s", mv_id, model, version)
#     logging.info("Data profiling status: %s", res)
