import click

from kafka.errors import NoBrokersAvailable, IllegalStateError

from hydroserving.cli.dev.dev_group import dev
from hydroserving.cli.utils import ensure_kafka_params
from hydroserving.constants.help import *
from hydroserving.helpers.kafka_helper import kafka_send, topic_offsets, consumer_with_offsets
from hydroserving.helpers.proto import messages_from_file, to_json_string
from hydroserving.models.kafka_params import KafkaParams


@dev.group(help=KAFKA_HELP)
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
    except NoBrokersAvailable:
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
    except NoBrokersAvailable:
        click.echo("Couldn't read messages. No brokers available: {}".format(params.brokers))
    except IllegalStateError as e:
        click.echo("Couldn't read messages. {}".format(e))
    except Exception as e:
        click.echo("Couldn't read messages. Unknown exception: {}".format(e))
    finally:
        if consumer is not None:
            consumer.close()
