from typing import List, Tuple, Callable, Optional
import logging
import functools

from hydrosdk.application import Application, ApplicationBuilder, ExecutionStageBuilder
from hydrosdk.deployment_configuration import DeploymentConfiguration
from hydrosdk.modelversion import ModelVersion
from hydrosdk.builder import AbstractBuilder
from hydrosdk.cluster import Cluster

from hydroserving.util.parseutil import _parse_model_reference, fill_arguments
from hydroserving.core.apply.context import ApplyContext


def parse_application(in_dict: dict) -> Callable[[Cluster], Application]:
    
    class LocalBuilder(AbstractBuilder):
        def __init__(self, in_dict: dict):
            self.in_dict = in_dict
        
        def build(self, cluster: Cluster, **kwargs) -> Application:
            logging.info("Parsing an application definition")

            apply_context: ApplyContext = kwargs.get("apply_context", ApplyContext())
            logging.debug(f"Apply context: {apply_context.to_dict()}")

            name = _parse_name(self.in_dict)
            singular_def = self.in_dict.get("singular")
            pipeline_def = self.in_dict.get("pipeline")

            if singular_def and pipeline_def:
                logging.error("Both singular and pipeline definitions are provided")
                raise SystemExit(1)

            if singular_def:
                logging.debug("Detected a singular app definition, parsing")
                model_version, config = _parse_singular_def(cluster, singular_def, apply_context)
                app_builder = ApplicationBuilder(name)
                stage = ExecutionStageBuilder() \
                    .with_model_variant(model_version, weight=100, deployment_configuration=config) \
                    .build()
                return app_builder.with_stage(stage).build(cluster)

            elif pipeline_def:
                logging.debug("Detected a pipeline app definition, parsing")
                pipeline = _parse_pipeline_def(cluster, pipeline_def, apply_context)
                app_builder = ApplicationBuilder(name)
                stages = []
                for stage in pipeline:
                    stage_builder = ExecutionStageBuilder()
                    for (model_version, config), weight in stage:
                        stage_builder.with_model_variant(model_version, weight, config)
                    stages.append(stage_builder.build())
                for stage in stages:
                    app_builder.with_stage(stage)
                return app_builder.build(cluster)

            else:
                logging.error("Neither singular nor pipeline fields are defined")
                raise SystemExit(1)
    
    return functools.partial(
        fill_arguments,
        lambda **kwargs: LocalBuilder(in_dict),
    )

def _parse_singular_def(cluster: Cluster, in_dict: dict, apply_context: ApplyContext) -> Tuple[ModelVersion, Optional[DeploymentConfiguration]]:
    """
    singular: 
      model: identity:1
    """
    reference = in_dict.get("model")
    if reference is None:
        logging.error("Couldn't find model field")
        raise SystemExit(1)
    model_version = apply_context.parse_model_version(reference)
    if model_version is None:
        name, version = _parse_model_reference(reference)
        model_version = ModelVersion.find(cluster, name, version)
    logging.debug(f"Found model: {model_version}")
    config = None
    if in_dict.get("deployment-configuration"):
        config = apply_context.parse_deployment_configuration(in_dict["deployment-configuration"])
        if config is None:
            config = DeploymentConfiguration.find(cluster, in_dict["deployment-configuration"])
        logging.debug(f"Found deployment configuration: {config}")
    return model_version, config


def _parse_name(in_dict: dict) -> str:
    logging.debug(f"Parsing name")
    if in_dict.get('name') is None:
        logging.error("Couldn't find name field")
        raise SystemExit(1)
    name = in_dict["name"]
    logging.debug(f"Parsed name: {name}")
    return name


def _parse_weight(in_dict: dict) -> int:
    return int(in_dict.get("weight", 100))


def _parse_pipeline_def(cluster: Cluster, items: list, apply_context: ApplyContext) -> List[List[Tuple[Tuple[ModelVersion, Optional[DeploymentConfiguration]], int]]]:
    """
    pipeline:
      - - model: identity-prep:1
      - - model: identity:1
          weight: 80
        - model: identity:2
          weight: 20
    """
    pipeline = []
    for i, stage in enumerate(items):
        variants = []
        for j, variant in enumerate(stage):
            result = (_parse_singular_def(cluster, variant, apply_context), _parse_weight(variant))
            logging.debug(f"Parsed variant ({j}) in a stage ({i}): {result}")
            variants.append(result)
        logging.debug(f"Total number of variants in a stage ({i}): {len(variants)}")
        pipeline.append(variants)
    logging.debug(f"Total number of stages: {len(pipeline)}")
    return pipeline
