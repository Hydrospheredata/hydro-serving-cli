from abc import ABC, abstractmethod

from hydroserving.httpclient.api import CreateApplicationRequest, KafkaStreamingParams, ModelServiceRequest, \
    ApplicationExecutionGraphRequest, ApplicationStageRequest


class ExecutionGraphLike(ABC):
    @abstractmethod
    def to_create_request(self, id_mapper):
        """

        Args:
            id_mapper (dict):
        """
        pass


class ModelService(ExecutionGraphLike):
    def __init__(self, model_version, runtime, weight, environment):
        """

        Args:
            environment (str or None):
            weight (int):
            runtime (str):
            model_version (str):
        """
        self.weight = weight
        self.model_version = model_version
        self.runtime = runtime
        self.environment = environment

    def to_create_request(self, id_mapper):
        request = ModelServiceRequest(
            model_version_id=id_mapper[self.model_version],
            runtime_id=id_mapper[self.runtime],
            environment_id=None,
            signature_name=None,
            weight=None
        )
        if self.environment is not None:
            request.environmentId = id_mapper[self.environment]
        if self.weight is not None:
            request.weight = self.weight

        return request


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
            environment=environment
        )
        self.monitoring_params = monitoring_params

    def to_create_request(self, id_mapper):
        return self.as_pipeline().to_create_request(id_mapper)

    def as_pipeline(self):
        """
        Wraps singular model as complete pipeline.
        Returns:
            Pipeline:
        """
        fict_pipeline = Pipeline([
            PipelineStage(
                services=[self.model_service],
                monitoring=self.monitoring_params,
                signature="signature-to-be-ignored"
            )
        ])
        return fict_pipeline


class PipelineStage(ExecutionGraphLike):
    def __init__(self, services, monitoring, signature):
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

    def to_create_request(self, id_mapper):
        stage_services = []
        for service in self.services:
            service_repr = service.to_create_request(id_mapper)
            service_repr.signatureName = self.signature
            stage_services.append(service_repr)
        return ApplicationStageRequest(stage_services)


class Pipeline(ExecutionGraphLike):
    def __init__(self, stages):
        """

        Args:
            stages (list of PipelineStage): 
        """
        self.stages = stages

    def to_create_request(self, id_mapper):
        stages = [x.to_create_request(id_mapper) for x in self.stages]

        return ApplicationExecutionGraphRequest(
            stages=stages
        )

    def as_pipeline(self):
        """

        Returns:
            Pipeline: returns self
        """
        return self


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
    def __init__(self, name, execution_graph, streaming_params):
        """

        Args:
            streaming_params (list of KafkaStreamingParams):
            execution_graph (SingularModel or Pipeline):
            name (str): 
        """
        if streaming_params is None:
            streaming_params = []
        self.streaming_params = streaming_params
        self.name = name
        self.execution_graph = execution_graph

    def to_create_request(self, id_mapper):
        return CreateApplicationRequest(
            name=self.name,
            kafka_streaming=self.streaming_params,
            execution_graph=self.execution_graph.to_create_request(id_mapper)
        )
