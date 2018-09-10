import os
import yaml


class ExecutionGraphLike:
    def to_graph(self):
        """
        Returns execution graph representation as dict
        :return: dict
        """
        raise NotImplementedError()

    @staticmethod
    def from_dict(data_dict):
        if data_dict is None:
            return None

        model_dict = data_dict.get("model")
        graph = data_dict.get("graph")

        if model_dict is not None and graph is not None:
            raise ValueError("Both model and graph are defined")

        if model_dict is not None:
            return Model(
                name=model_dict.get("name"),
                version=model_dict.get("version"),
                environment=model_dict.get("environment"),
                runtime=model_dict.get("runtime")
            )

        if graph is not None:
            pipeline_steps = []
            for stage in graph:
                new_stage = []
                for service in stage:
                    new_service = PipelineService(
                        name=service.get("name"),
                        version=service.get("version"),
                        runtime=service.get("runtime"),
                        weight=service.get("weight"),
                        signature=service.get("signature"),
                        environment=service.get("environment")
                    )
                    new_stage.append(new_service)
                pipeline_steps.append(new_stage)

            return Pipeline(
                steps=pipeline_steps
            )

        raise ValueError("Neither model nor graph are defined")


class Model(ExecutionGraphLike):
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


class PipelineService:
    def __init__(self, name, version, runtime, weight, signature, environment):
        self.signature = signature
        self.weight = weight
        self.version = version
        self.runtime = runtime
        self.name = name
        self.environment = environment


class Pipeline(ExecutionGraphLike):
    def __init__(self, steps):
        self.steps = steps

    def to_graph(self):
        new_stages = []
        for step in self.steps:
            new_services = []
            for service in step:
                service_def = {
                    "runtime": service.runtime,
                    "modelVersion": "{}:{}".format(service.name, service.version),
                    "weight": service.weight,
                    "environment": service.environment,
                    "signatureName": service.signature
                }
                new_services.append(service_def)
            new_stages.append({"services": new_services})

        return {"stages": new_stages}


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
    def __init__(self, name, dependencies=None, graph_like=None, kafka_streaming=None):
        self.kafka_streaming = kafka_streaming
        self.name = name
        self.graph_like = graph_like
        self.dependencies = dependencies

    def to_http_payload(self):
        return {
            "name": self.name,
            "executionGraph": self.graph_like.to_graph()
        }

    @staticmethod
    def from_dict(data_dict):
        if data_dict is None:
            return None

        app_dict = data_dict.get("application")
        return Application(
            name=app_dict.get("name"),
            dependencies=app_dict.get("dependencies"),
            graph_like=ExecutionGraphLike.from_dict(app_dict),
            kafka_streaming=KafkaStreamingParams.from_dict(app_dict)
        )

    @staticmethod
    def from_directory(directory_path):
        if not os.path.exists(directory_path):
            raise FileNotFoundError("{} doesn't exist".format(directory_path))
        if not os.path.isdir(directory_path):
            raise NotADirectoryError("{} is not a directory".format(directory_path))

        metafile = os.path.join(directory_path, "serving.yaml")
        if not os.path.exists(metafile):
            return None

        with open(metafile, "r") as serving_file:
            return Application.from_dict(yaml.load(serving_file.read()))
