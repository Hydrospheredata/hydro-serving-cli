import os
import yaml
from abc import ABC, abstractmethod


class ExecutionGraphLike(ABC):
    @abstractmethod
    def to_graph(self):
        """
        Return representation of graph as dict
        Returns:
            dict:
        """
        pass


class SingularApplication(ExecutionGraphLike):
    def __init__(self, name, version, runtime, environment):
        self.name = name
        self.version = version
        self.runtime = runtime
        self.environment = environment

    def to_graph(self):
        return {
            "stages": [{
                "services": [{
                    "runtime": self.runtime,
                    "modelVersion": "{}:{}".format(self.name, self.version),
                    "weight": 100,
                    "environment": self.environment
                }]
            }]
        }


class ModelService:
    def __init__(self, name, version, runtime, weight, signature, environment):
        """

        Args:
            environment (int or None): 
            signature (str): 
            weight (int): 
            runtime (str): 
            version (int): 
            name (str): 
        """
        self.signature = signature
        self.weight = weight
        self.version = version
        self.runtime = runtime
        self.name = name
        self.environment = environment


class PipelineStage:
    def __init__(self, name, services, monitoring, signature):
        """

        Args:
            signature (str): 
            monitoring (dict): 
            services (list of ModelService): 
            name (str): 
        """
        self.signature = signature
        self.monitoring = monitoring
        self.services = services
        self.name = name


class Pipeline(ExecutionGraphLike):
    def __init__(self, stages):
        """

        Args:
            stages (list of PipelineStage): 
        """
        self.stages = stages

    def to_graph(self):
        raise NotImplementedError()
        # new_stages = []
        # for step in self.stages:
        #     new_services = []
        #     for service in step:
        #         service_def = {
        #             "runtime": service.runtime,
        #             "modelVersion": "{}:{}".format(service.name, service.version),
        #             "weight": service.weight,
        #             "environment": service.environment,
        #             "signatureName": service.signature
        #         }
        #         new_services.append(service_def)
        #     new_stages.append({"services": new_services})
        #
        # return {"stages": new_stages}


class KafkaStreamingParams:
    def __init__(self, source_topic, destination_topic, error_topic, consumer_id):
        self.source_topic = source_topic
        self.destination_topic = destination_topic
        self.error_topic = error_topic
        self.consumer_id = consumer_id

    @staticmethod
    def from_dict(data_dict):
        if data_dict is None:
            return None

        kafka_dict = data_dict.get("kafka")
        return KafkaStreamingParams(
            source_topic=kafka_dict.get("source_topic"),
            destination_topic=kafka_dict.get("destination_topic"),
            error_topic=kafka_dict.get("error_topic"),
            consumer_id=kafka_dict.get("consumer_id")
        )


class Application:
    def __init__(self, name, graph_like=None, kafka_streaming=None):
        """

        Args:
            kafka_streaming (KafkaStreamingParams):
            graph_like (ExecutionGraphLike): 
            name (str): 
        """
        self.kafka_streaming = kafka_streaming
        self.name = name
        self.graph_like = graph_like

    def to_http_payload(self):
        return {
            "name": self.name,
            "executionGraph": self.graph_like.to_graph()
        }
