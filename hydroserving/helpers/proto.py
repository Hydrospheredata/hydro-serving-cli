import os

from google.protobuf.json_format import Parse, MessageToJson
from hydro_serving_grpc.kafka.kafka_messages_pb2 import KafkaServingMessage
import json

def messages_from_file(path):
    p = os.path.abspath(os.path.expanduser(path))
    f = open(p)
    json_message = f.read()
    f.close()
    messages = json.loads(json_message)
    if not isinstance(messages, list):
        messages = [messages]

    array = []

    for m in messages:
        array.append(parse_proto(json.dumps(m)))

    return array

def to_json_string(bytes):
    message = KafkaServingMessage()
    message.ParseFromString(bytes)
    json = MessageToJson(message)
    return json

def parse_proto(json_message):
    message = KafkaServingMessage()
    Parse(json_message, message)
    return message
