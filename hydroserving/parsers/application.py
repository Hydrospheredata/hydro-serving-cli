from collections import OrderedDict

from hydroserving.models.definitions.application import Application, SingularApplication, ModelService, Pipeline, \
    PipelineStage
from hydroserving.parsers.abstract import AbstractParser


class ApplicationParser(AbstractParser):
    def to_dict(self, obj):
        pass

    def parse_dict(self, in_dict):
        if in_dict is None:
            return None

        model_dict = in_dict.get("singular")
        pipeline = in_dict.get("pipeline")

        if model_dict is not None \
                and pipeline is not None:
            raise ValueError("Both model and graph are defined")

        if model_dict is not None:
            return SingularApplication(
                name=model_dict.get("name"),
                version=model_dict.get("version"),
                environment=model_dict.get("environment"),
                runtime=model_dict.get("runtime")
            )

        if pipeline is not None:
            if not isinstance(pipeline, dict):
                raise TypeError("Invalid pipeline definition. Must be dictionary.", pipeline)
            sorted_pipeline_config = OrderedDict(sorted(pipeline.items(), key=lambda t: t[0]))
            pipeline_stages = []

            for key, stage in sorted_pipeline_config.items():
                monitoring = stage.get("monitoring")
                if monitoring is not None:
                    pass  # fill monitoring params
                signature = stage['signature']

                services = []
                service_defs = stage['definition']
                for service in service_defs:
                    new_service = ModelService(
                        name=service["name"],
                        version=service["version"],
                        runtime=service["runtime"],
                        weight=service["weight"],
                        signature=signature,
                        environment=service.get("environment")
                    )
                    services.append(new_service)
                pipeline_stages.append(
                    PipelineStage(
                        name=key,
                        services=services,
                        monitoring=None,
                        signature=signature
                    )
                )

            return Pipeline(
                stages=pipeline_stages
            )

        raise ValueError("Neither model nor graph are defined")
