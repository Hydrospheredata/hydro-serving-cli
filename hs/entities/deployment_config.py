from hs.metadata_collectors.collected_metadata import CollectedMetadata
from pydantic.main import BaseModel
from typing import Optional

from hydrosdk.cluster import Cluster
from hydrosdk.deployment_configuration import DeploymentConfigurationBuilder, ContainerSpec, \
    PodSpec, DeploymentSpec, HorizontalPodAutoScalerSpec

class DeploymentConfig(BaseModel):
    name: str
    container: Optional[ContainerSpec]
    pod: Optional[PodSpec]
    deployment: Optional[DeploymentSpec]
    hpa: Optional[HorizontalPodAutoScalerSpec]

    class Config:
        @staticmethod
        def to_camel_case(x: str):
            segments = x.split("_")
            return segments[0] + "".join([x.capitalize() for x in segments[1:]])

        alias_generator = to_camel_case
        allow_population_by_field_name = True

    def apply(self, conn: Cluster):
        builder = DeploymentConfigurationBuilder(self.name)
        builder._with_container_spec(self.container)
        builder._with_pod_spec(self.pod)
        builder._with_deployment_spec(self.deployment)
        builder._with_hpa_spec(self.hpa)
        print(builder)
        return builder.build(conn)