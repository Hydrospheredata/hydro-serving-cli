from hydroserving.httpclient.api import KafkaStreamingParams
from hydroserving.models.definitions.application import Application, SingularModel, ModelService, Pipeline, \
    PipelineStage, MonitoringParams
from hydroserving.parsers.abstract import AbstractParser


class ApplicationParser(AbstractParser):
    @staticmethod
    def parse_streaming_params(in_list):
        """

        Args:
            in_list (list of dict):

        Returns:
            StreamingParams:
        """
        params = []
        for item in in_list:
            params.append(KafkaStreamingParams(
                source_topic=item["in-topic"],
                destination_topic=item["out-topic"]
            ))
        return params

    @staticmethod
    def streaming_to_dict(streaming_params):
        """

        Args:
            streaming_params (StreamingParams):
        """
        return {
            'sourceTopic': streaming_params.source_topic,
            'destinationTopic': streaming_params.destination_topic
        }

    @staticmethod
    def parse_monitoring_param_list(in_list):
        """

        Args:
            in_list (list of dict): 

        Returns:
            list of MonitoringParams: 
        """
        if in_list is None:
            return []
        result = [
            ApplicationParser.parse_monitoring_params(x)
            for x in in_list
        ]
        return result

    @staticmethod
    def parse_monitoring_params(in_dict):
        """

        Args:
            in_dict (dict):

        Returns:
            MonitoringParams:
        """
        if in_dict is None:
            return None
        healthcheck_params = in_dict.get('healthcheck')
        params = MonitoringParams(
            name=in_dict['name'],
            input=in_dict['input'],
            type=in_dict['type'],
            app=in_dict.get('app'),
            healthcheck_on=False,
            threshold=None
        )
        if healthcheck_params is not None:
            params.healthcheck_on = healthcheck_params.get("enabled", False)
            params.threshold = healthcheck_params.get("threshold")
        return params

    @staticmethod
    def parse_singular(in_dict):
        return SingularModel(
            model_version=in_dict['model'],
            runtime=in_dict['runtime'],
            environment=in_dict.get("environment"),
            monitoring_params=ApplicationParser.parse_monitoring_param_list(in_dict.get("monitoring"))
        )

    @staticmethod
    def parse_model_service_list(in_list):
        services = [
            ApplicationParser.parse_model_service(x)
            for x in in_list
        ]
        return services

    @staticmethod
    def parse_model_service(in_dict):
        return ModelService(
            model_version=in_dict['model'],
            runtime=in_dict['runtime'],
            weight=in_dict['weight'],
            environment=in_dict.get("environment")
        )

    @staticmethod
    def parse_pipeline_stage(stage_dict):
        monitoring = ApplicationParser.parse_monitoring_param_list(stage_dict.get("monitoring", []))
        signature = stage_dict['signature']
        multi_services = stage_dict.get('modelservices')
        if multi_services is not None:
            services = ApplicationParser.parse_model_service_list(multi_services)
        else:
            services = [
                ModelService(
                    model_version=stage_dict['model'],
                    runtime=stage_dict['runtime'],
                    weight=100,
                    environment=stage_dict.get('environment')
                )
            ]
        return PipelineStage(
            services=services,
            monitoring=monitoring,
            signature=signature
        )

    @staticmethod
    def parse_pipeline(in_list):
        pipeline_stages = []
        for i, stage in enumerate(in_list):
            pipeline_stages.append(ApplicationParser.parse_pipeline_stage(stage))
        return Pipeline(pipeline_stages)

    def parse_dict(self, in_dict):
        if in_dict is None:
            return None

        streaming_params = None

        singular_def = in_dict.get("singular")
        pipeline_def = in_dict.get("pipeline")
        streaming_def = in_dict.get('streaming')

        if streaming_def is not None:
            streaming_params = self.parse_streaming_params(streaming_def)

        if singular_def is not None \
                and pipeline_def is not None:
            raise ValueError("Both singular and pipeline definitions are provided")

        if singular_def is not None:
            execution_graph = self.parse_singular(singular_def)
        elif pipeline_def is not None:
            execution_graph = self.parse_pipeline(pipeline_def)
        else:
            raise ValueError("Neither model nor graph are defined")

        return Application(
            name=in_dict['name'],
            execution_graph=execution_graph,
            streaming_params=streaming_params
        )

    def to_dict(self, obj):
        """

        Args:
            obj (Application):
        """
        return {
            "name": obj.name,
            'kafkaStreaming': self.streaming_to_dict(obj.streaming_params),
            "executionGraph": obj.execution_graph.to_graph_repr()
        }
