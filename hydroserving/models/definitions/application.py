from abc import ABC, abstractmethod


class ExecutionGraphLike(ABC):
    @abstractmethod
    def to_graph_repr(self):
        """
        Return representation of graph as dict
        Returns:
            dict:
        """
        pass


class ModelService(ExecutionGraphLike):
    def __init__(self, model_version, runtime, weight, signature, environment):
        """

        Args:
            environment (int or None):
            signature (str or None):
            weight (int):
            runtime (str):
            model_version (str):
        """
        self.signature = signature
        self.weight = weight
        self.model_version = model_version
        self.runtime = runtime
        self.environment = environment

    def to_graph_repr(self):
        fields = {
            "runtime": self.runtime,
            "modelVersion": self.model_version,
            "weight": self.weight,
        }
        if self.environment is not None:
            fields["environment"] = self.environment
        if self.signature is not None:
            fields["signatureName"] = self.signature

        return fields


class SingularModel(ExecutionGraphLike):
    def __init__(self, model_version, runtime, environment, monitoring_params):
        """

        Args:
            model_version (str):
            runtime (str):
            environment (str or None):
            monitoring_params (list of MonitoringParams):
        """
        self.model_service = ModelService(
            model_version=model_version,
            runtime=runtime,
            weight=100,
            signature=None,
            environment=environment
        )
        self.monitoring_params = monitoring_params

    def to_graph_repr(self):
        return {
            "stages": [{
                "services": [
                    self.model_service.to_graph_repr()
                ]
            }]
        }


class PipelineStage(ExecutionGraphLike):
    def __init__(self, name, services, monitoring, signature):
        """

        Args:
            signature (str): 
            monitoring (list of MonitoringParams):
            services (list of ModelService): 
            name (str): 
        """
        self.signature = signature
        self.monitoring = monitoring
        self.services = services
        self.name = name

    def to_graph_repr(self):
        dict_services = []
        for service in self.services:
            service_repr = service.to_graph_repr()
            service_repr['signature'] = self.signature
            dict_services.append(service_repr)
        return {
            'services': dict_services
        }


class Pipeline(ExecutionGraphLike):
    def __init__(self, stages):
        """

        Args:
            stages (list of PipelineStage): 
        """
        self.stages = stages

    def to_graph_repr(self):
        stages = [x.to_graph_repr() for x in self.stages]
        return {
            'stages': list(stages)
        }


class StreamingParams:
    def __init__(self, source_topic, destination_topic):
        """

        Args:
            destination_topic (str):
            source_topic (str):
        """
        self.source_topic = source_topic
        self.destination_topic = destination_topic


class MonitoringParams:
    def __init__(self, name, input, type, app, healthcheck_on, threshold):
        """

        Args:
            threshold (float or None):
            healthcheck_on (bool):
            app (str):
            type (str):
            input (str):
            name (str):
        """
        self.threshold = threshold
        self.healthcheck_on = healthcheck_on
        self.app = app
        self.type = type
        self.input = input
        self.name = name


class Application:
    def __init__(self, name, execution_graph, streaming_params=None):
        """

        Args:
            streaming_params (StreamingParams):
            execution_graph (SingularModel or Pipeline):
            name (str): 
        """
        self.streaming_params = streaming_params
        self.name = name
        self.execution_graph = execution_graph
