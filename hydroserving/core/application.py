from abc import ABC, abstractmethod

from hydroserving.serving_api.api import CreateApplicationRequest, KafkaStreamingParams, ModelServiceRequest, \
    ApplicationExecutionGraphRequest, ApplicationStageRequest


class ExecutionGraphLike(ABC):
    @abstractmethod
    def to_create_request(self, id_mapper):
        """

        Args:
            id_mapper (dict):
        """
        pass


class ModelVariant(ExecutionGraphLike):
    def __init__(self, model_version, runtime, weight, environment):
        """

        Args:
            weight (int):
            model_version (str):
        """
        self.weight = weight
        self.model_version = model_version


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
        self.model_service = ModelVariant(
            model_version=model_version,
            weight=100
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

class ModelVariant:
    def __init__(self, model_version_id, runtime_id, environment_id, signature_name, weight):
        """

        Args:
            weight (int or None): from 100 to 0
            signature_name (str or None):
            environment_id (int or None):
            runtime_id (int):
            model_version_id (int):
        """
        self.weight = weight
        self.signatureName = signature_name
        self.environmentId = environment_id
        self.runtimeId = runtime_id
        self.modelVersionId = model_version_id


class GraphStage:
    def __init__(self, services):
        """

        Args:
            services (list of ModelVariant):
        """
        self.services = services


class executionGraph:
    def __init__(self, stages):
        """

        Args:
            stages (list of GraphStage):
        """
        self.stages = stages


class KafkaStreamingParams:
    def __init__(self, source_topic, destination_topic):
        """

        Args:
            destination_topic (str): 
            source_topic (str): 
        """
        self.destinationTopic = destination_topic
        self.sourceTopic = source_topic


class CreateApplicationRequest:
    def __init__(self, name, execution_graph, kafka_streaming):
        """

        Args:
            kafka_streaming (list of KafkaStreamingParams):
            execution_graph (ApplicationExecutionGraphRequest): 
            name (str): 
        """
        self.kafkaStreaming = kafka_streaming
        self.executionGraph = execution_graph
        self.name = name


class ApplicationService:
    def __init__(self, connection):
        self.connection = connection

    def create(self, application):
        """

        Args:
            application (CreateApplicationRequest):

        Returns:
            dict
        """
        return self.connection.post("/api/v1/applications", application.__dict__)

    def update(self, id, application):
        update_req = application.__dict__
        update_req['id'] = int(id)
        return self.connection.put('/api/v1/applications', update_req)

    def serve(self, app_name, signature_name, data):
        """

        Args:
            data (dict):
            signature_name (str):
            app_name (str):

        Returns:
            dict:
        """
        return self.connection.post(
            "/api/v1/applications/serve/{0}/{1}".format(app_name, signature_name),
            data
        )

    def list(self):
        """

        Returns:
            list of dict:
        """
        return self.connection.get("/api/v1/applications")

    def find(self, app_name):
        """

        Args:
            app_name (str):
        """
        for app in self.list():
            if app['name'] == app_name:
                return app
        return None