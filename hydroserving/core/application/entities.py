from enum import Enum
from collections import namedtuple


class ApplicationStatus(Enum):
    Assembling = "Assembling"
    Ready = "Ready"
    Failed = "Failed"


def model_variant(model_version_id, weight=100):
    return {
        'modelVersionId': model_version_id,
        'weight': weight
    }


def pipeline_stage(variants):
    weights = [x['weight'] for x in variants]
    if weights != 100:
        raise ValueError("ModelVariant weights should add up to 100 inside one stage")
    return {
        "model_variants": variants
    }


def pipeline(stages):
    return {
        "stages": stages
    }


def streaming_params(in_topic, out_topic):
    return {
        'sourceTopic': in_topic,
        'destinationTopic': out_topic
    }


def app_creation_request(name, executionGraph, kafka_params):
    return {
        "name": name,
        "executionGraph": executionGraph,
        "kafkaStreaming": kafka_params
    }


ApplicationDef = namedtuple('ApplicationDef', ('name', 'execution_graph', 'kafka_streaming'))
