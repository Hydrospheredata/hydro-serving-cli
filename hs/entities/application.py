from hs.metadata_collectors.collected_metadata import CollectedMetadata
import logging
from typing import Dict, List, Optional
from pydantic import root_validator

from hydrosdk.cluster import Cluster
from hydrosdk.exceptions import HydrosphereException
from hydrosdk.modelversion import ModelVersion
from hydrosdk.application import Application as HS_APP, ApplicationBuilder, ExecutionStage, ModelVariant
from hs.entities.base_entity import BaseEntity

class WeightedStage(BaseEntity):
    model: str
    weight: Optional[int] = 100
    deployment_config: Optional[str]

class SingularStage(BaseEntity):
    model: str
    deployment_config: Optional[str]

class Application(BaseEntity):
    name: str
    metadata: Optional[Dict[str, str]]
    """
    Need to choose singular or pipline
    """
    singular: Optional[SingularStage]
    pipeline: Optional[List[List[WeightedStage]]]

    @root_validator(pre=True)
    def app_validator(cls, values):
        def_exists = ('singular' in values) or ('pipeline' in values)
        assert def_exists, "Invalid application: no 'singular' or 'pipeline' fields"
        both_exist = ('singular' in values) and ('pipeline' in values)
        assert not both_exist, "Invalid application: can't have both 'singular' and 'pipeline' fields"
        return values

    def app_builder(self, conn: Cluster, metadata: Dict[str, str]) -> ApplicationBuilder:
        builder = ApplicationBuilder(self.name)
        if self.metadata:
            metadata.update(self.metadata)
        builder.with_metadatas(metadata)
        if self.singular:
            name, version = self.singular.model.split(":")
            mv = ModelVersion.find(conn, name, version)
            builder.with_stage(ExecutionStage(signature = None, model_variants = [ModelVariant(
                modelVersionId = mv.id,
                weight = 100,
                deploymentConfigurationName = self.singular.deployment_config
            )]))
        elif self.pipeline:
            for stage in self.pipeline:
                variants: List[ModelVariant] = []
                for model in stage:
                    name, version = model.model.split(":")
                    mv = ModelVersion.find(conn, name, version) 
                    variants.append(
                        ModelVariant(
                            modelVersionId = mv.id,
                            weight = model.weight,
                            deploymentConfigurationName = model.deployment_config
                        )
                    )
                builder.with_stage(ExecutionStage(signature = None, model_variants = variants))
        else:
            raise ValueError("Invalid application: no 'singular' or 'pipeline' fields")
        return builder

    def apply(self, conn: Cluster, cwd) -> HS_APP:
        collected_meta = CollectedMetadata.collect(cwd).to_metadata()
        builder = self.app_builder(conn, collected_meta)
        found_app = None
        try:
            found_app = HS_APP.find(conn, self.name)
        except HydrosphereException:
            logging.debug(f"Can't get an application {self.name} from cluster", exc_info=True)
            pass
        if found_app:
            logging.info(f"Found existing application {found_app.name}. Updating it.")
            HS_APP.delete(conn, self.name)

        app = builder.build(conn)
        return app