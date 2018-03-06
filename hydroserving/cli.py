import docker
from kafka.errors import NoBrokersAvailable, IllegalStateError

from hydroserving.helpers.kafka_helper import kafka_send, topic_offsets, consumer_with_offsets
from hydroserving.helpers.proto import messages_from_file, to_json_string
from hydroserving.helpers.assembly import assemble_model
from hydroserving.helpers.deployment import *
from hydroserving.helpers.package import read_contract_cwd, build_model
from hydroserving.helpers.upload import upload_model
from hydroserving.httpclient.api import ModelAPI
from hydroserving.constants.help import *
from hydroserving.httpclient.remote_connection import RemoteConnection
from hydroserving.models import FolderMetadata
from hydroserving.models.context_object import ContextObject
from hydroserving.models.kafka_params import KafkaParams


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
    remote = RemoteConnection("http://{}:{}".format(host, port))
    model_api = ModelAPI(remote)
    result = upload_model(model_api, source, metadata.model)
    click.echo(result)


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


@hs_cli.group(help=KAFKA_HELP)
@click.option('--brokers',
              help=KAFKA_ADVERTISED_ADDR_HELP,
              type=str,
              required=True)
@click.option('--topic',
              help=KAFKA_TOPIC_HELP,
              type=str,
              required=True)
@click.pass_context
def kafka(ctx, brokers, topic):
    ctx.obj.kafka_params = KafkaParams(brokers, topic)


@kafka.command(help=PUBLISH_TO_KAFKA_HELP)
@click.option('--file',
              help=KAFKA_PREDICT_REQUEST_FILE_HELP,
              type=click.Path(),
              required=True)
@click.pass_obj
def publish(obj, file):
    params = ensure_kafka_params(obj)
    click.echo("publishing message to kafka")
    try:
        messages = messages_from_file(file)
        for message in messages:
            future = kafka_send(params.brokers, params.topic, message.SerializeToString())
            result = future.get(timeout=60)
            click.echo("published: {}".format(result))
    except NoBrokersAvailable as e:
        click.echo("Couldn't publish message. No brokers available: {}".format(kafka))
    except IllegalStateError as e:
        click.echo("Couldn't publish message: {}".format(e))
    except Exception as e:
        click.echo("Couldn't publish message. Unknown exception: {}".format(e))


@kafka.command(help=READ_FROM_KAFKA_HELP)
@click.option('--tail',
              help=KAFKA_TAIL_HELP,
              type=int,
              default=10,
              required=False)
@click.pass_obj
def read(obj, tail):
    params = ensure_kafka_params(obj)
    click.echo("reading message from kafka:")
    consumer = None
    try:
        offsets = topic_offsets(params.brokers, params.topic)
        click.echo("topics and offsets statistics:")
        for k, v in offsets.items():
            click.echo(
                "\ttopic_partition({} - {}).............................. offset:{}".format(k.topic, k.partition, v))

        consumer = consumer_with_offsets(params.brokers, offsets, tail)
        for msg in consumer:
            kafka_msg = to_json_string(msg.value)
            click.echo("\n\n\n\ntopic_partition({}:{}) with offset:{}".format(msg.topic, msg.partition, msg.offset))
            click.echo("\n{}".format(kafka_msg))
    except NoBrokersAvailable as e:
        click.echo("Couldn't read messages. No brokers available: {}".format(params.brokers))
    except IllegalStateError as e:
        click.echo("Couldn't read messages. {}".format(e))
    except Exception as e:
        click.echo("Couldn't read messages. Unknown exception: {}".format(e))
    finally:
        if consumer is not None:
            consumer.close()


def ensure_metadata(obj):
    if obj.metadata is None:
        click.echo("Directory doesn't have a serving metadata")
        raise SystemExit(-1)
    return obj.metadata


def ensure_kafka_params(obj):
    if obj.kafka_params is None:
        click.echo("Kafka params aren't specified")
        raise SystemExit(-1)
    return obj.kafka_params
