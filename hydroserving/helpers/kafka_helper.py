from kafka import KafkaProducer, SimpleClient, KafkaConsumer
from kafka.structs import OffsetRequestPayload, TopicPartition


class KafkaException(Exception):
    def __init__(self, message, errors):

        super(KafkaException, self).__init__(message)

        self.errors = errors

def insure_is_array(bootstrap_servers):
    if isinstance(bootstrap_servers, str):
        bootstrap_servers = bootstrap_servers.replace(" ","").split(",")
    if not isinstance(bootstrap_servers, list):
        raise KafkaException("kafka_brokers should be str or list[str]")

    return bootstrap_servers


def kafka_send(kafka_brokers, topic, message):
    producer = KafkaProducer(bootstrap_servers=insure_is_array(kafka_brokers))
    result = producer.send(topic=topic, value=message)
    producer.close()
    return result

def topic_offsets(kafka_brokers, topic):
    client = SimpleClient(insure_is_array(kafka_brokers))
    topic_partitions = client.topic_partitions
    if not topic in topic_partitions:
       raise KafkaException("topic {} doesn't exists".format(topic))
    partitions = topic_partitions[topic]
    offset_requests = [OffsetRequestPayload(topic, p, -1, 1) for p in partitions.keys()]
    offsets_responses = client.send_offset_request(offset_requests)
    client.close()
    partitions_and_offsets = {}
    for offset in offsets_responses:
        if offset.topic == topic:
            topic_offset = 0
            topic_partition = TopicPartition(topic = offset.topic, partition=offset.partition)
            if offset.offsets[0]:
                topic_offset = offset.offsets[0]
            partitions_and_offsets[topic_partition] = topic_offset

    return partitions_and_offsets

def consumer_with_offsets(kafka_brokers, offsets, tail):
    dict_size = len(offsets)
    ceil = int(tail / dict_size)
    diff = tail % dict_size
    new_offsets = {}
    for k, v in offsets.items():
        new_val = 0
        if v > diff:
            new_val = v - ceil
        if new_val != 0 and diff != 0:
            new_val -= 1
            diff -= 1
        new_offsets[k] = new_val

    consumer = KafkaConsumer(bootstrap_servers=insure_is_array(kafka_brokers))
    consumer.assign(new_offsets.keys())
    for k, v in new_offsets.items():
        consumer.seek(k, v)
    return consumer




