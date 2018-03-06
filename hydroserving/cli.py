import docker
import sys
from kafka.errors import NoBrokersAvailable, IllegalStateError

from hydroserving.httpclient.api import ModelAPI
from hydroserving.constants.help import *
from hydroserving.helpers.assembly import assemble_model
from hydroserving.helpers.deployment import *
from hydroserving.helpers.package import read_contract_cwd, build_model
from hydroserving.helpers.upload import upload_model
from hydroserving.models import FolderMetadata
from hydroserving.models.context_object import ContextObject


@click.group()
@click.pass_context
def hs_cli(ctx):
    ctx.obj = ContextObject()
    metadata = FolderMetadata.from_directory(os.getcwd())
    ctx.obj.metadata = metadata


@hs_cli.command(help=STATUS_HELP)
@click.pass_obj
def status(obj):
    metadata = obj.metadata
    if metadata is None:
        click.echo("Directory doesn't have a serving metadata")
    else:
        click.echo("Detected a model: {}".format(metadata.model.name))
        click.echo("Model type: {}".format(metadata.model.model_type))
        click.echo("Files to upload:\n{}".format(metadata.model.payload))


@hs_cli.command()
@click.pass_obj
def pack(obj):
    metadata = ensure_metadata(obj)
    payload = pack_model(metadata.model)
    click.echo("Done. Packed: {}".format(payload))


@hs_cli.command()
@click.pass_obj
def assemble(obj):
    metadata = ensure_metadata(obj)
    assemble_model(metadata.model)
    click.echo("Done")


@hs_cli.command()
@click.pass_obj
def contract(obj):
    metadata = ensure_metadata(obj)
    click.echo("Reading contract...")
    contract_obj = read_contract_cwd(metadata.model)
    click.echo(contract_obj)


@hs_cli.command(help=UPLOAD_HELP, context_settings=CONTEXT_SETTINGS)
@click.option('--host',
              default="localhost",
              show_default=True,
              help=UPLOAD_HOST_HELP,
              required=False)
@click.option('--port',
              default=9090,
              show_default=True,
              help=UPLOAD_PORT_HELP,
              required=False)
@click.option('--source',
              help=UPLOAD_SOURCE_HELP,
              required=False)
@click.pass_obj
def upload(obj, host, port, source):
    metadata = ensure_metadata(obj)
    model_api = ModelAPI("http://{}:{}".format(host, port))
    result = upload_model(model_api, source, metadata.model)
    click.echo(result.text)


# LOCAL DEPLOYMENT COMMANDS

@hs_cli.group(help=LOCAL_HELP)
@click.pass_context
def local(ctx):
    ctx.obj.docker_client = docker.from_env()


@local.command(help=START_HELP)
@click.pass_obj
def start(obj):
    metadata = ensure_metadata(obj)
    click.echo("Deploying model in runtime...")
    docker_client = obj.docker_client
    build_model(metadata)
    start_runtime(metadata, docker_client)


@local.command(help=STOP_HELP)
@click.pass_obj
def stop(obj):
    metadata = ensure_metadata(obj)
    docker_client = obj.docker_client
    stop_runtime(metadata, docker_client)


def ensure_metadata(obj):
    if obj.metadata is None:
        click.echo("Directory doesn't have a serving metadata")
        raise SystemExit(-1)
    return obj.metadata


@hs_cli.group(help=KAFKA_HELP)
@click.pass_context
def kafka(ctx):
    ctx.obj.docker_client = docker.from_env()


@kafka.command(help=PUBLISH_TO_KAFKA_HELP)
@click.option('--kafka',
              help=KAFKA_ADVERTISED_HOST_AND_PORT_HELP,
              type=str,
              required=True)
@click.option('--topic',
              help=TOPIC_HELP,
              type=str,
              required=True)
@click.option('--file',
              help=PREDICT_REQUEST_FILE_HELP,
              type=click.Path(),
              required=True)
@click.pass_obj
def publish(obj, kafka, topic, file):
    click.echo("publishing message to kafka")
    try:
        messages = messages_from_file(file)
        for message in messages:
            future = kafka_send(kafka, topic, message.SerializeToString())
            result = future.get(timeout=60)
            click.echo("published: {}".format(result))
    except NoBrokersAvailable as e:
        click.echo("Couldn't publish message. No brokers available: {}".format(kafka))
    except IllegalStateError as e:
        click.echo("Couldn't publish message: {}".format(e))
    except:
        click.echo("Couldn't publish message. Unknown exception: {}".format(sys.exc_info()[0]))



@kafka.command(help=READ_FROM_KAFKA_HELP)
@click.option('--kafka',
              type=str,
              help=KAFKA_ADVERTISED_HOST_AND_PORT_HELP,
              required=True)
@click.option('--topic',
              help=TOPIC_HELP,
              type=str,
              required=True)
@click.option('--tail',
              help=TAIL_HELP,
              type=int,
              default=10,
              required=False)
@click.pass_obj
def read(obj, kafka, topic, tail):
    click.echo("reading message from kafka:")
    try:
        offsets = topic_offsets(kafka, topic)
        click.echo("topics and offsets statistics:")
        for k, v in offsets.items():
            click.echo("\ttopic_partition({} - {}).............................. offset:{}".format(k.topic, k.partition, v))

        consumer = consumer_with_offsets(kafka, offsets, tail)
        for msg in consumer:
            kafka_msg = to_json_string(msg.value)
            click.echo("\n\n\n\ntopic_partition({}:{}) with offset:{}".format(msg.topic, msg.partition, msg.offset))
            click.echo("\n{}".format(kafka_msg))
    except NoBrokersAvailable as e:
        click.echo("Couldn't read messages. No brokers available: {}".format(kafka))
    except IllegalStateError as e:
        click.echo("Couldn't read messages. {}".format(e))
    except:
        click.echo("Couldn't read messages. Unknown exception: {}".format(sys.exc_info()[0]))
    consumer.close()





