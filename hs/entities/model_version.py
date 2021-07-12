from hs.util.dockerutils import DockerLogHandler
import logging

from hydrosdk.image import DockerImage
from hs.entities.base_entity import BaseEntity
from typing import Dict, List, Optional, Union
from hs.entities.contract import Contract
from hs.metadata_collectors.collected_metadata import CollectedMetadata

from hydrosdk.cluster import Cluster
from hydrosdk.modelversion import ModelVersionBuilder, ModelVersion as SDK_MV, MonitoringConfiguration as SDK_MC
from hydrosdk.monitoring import MetricSpecConfig, MetricSpec

class MonitoringConfiguration(BaseEntity):
    batch_size: int

class MetricConfig(BaseEntity):
    monitoring_model: str
    threshold: Optional[Union[float, int]]
    operator: Optional[str]

class Metric(BaseEntity):
    name: str
    config: MetricConfig

class ModelVersion(BaseEntity):
    name: str
    runtime: str
    install_command: Optional[str]
    training_data: Optional[str]
    payload: List[str]
    contract: Contract
    monitoring: Optional[List[Metric]]
    metadata: Optional[Dict[str, str]]
    monitoring_configuration: Optional[MonitoringConfiguration]

    def apply(self, conn: Cluster, cwd):
        mv_builder = ModelVersionBuilder(name = self.name,path = cwd) \
            .with_runtime(DockerImage.from_string(self.runtime)) \
            .with_payload(self.payload) \
            .with_signature(self.contract.to_proto())

        if self.install_command:
            mv_builder.with_install_command(self.install_command)

        if self.training_data:
            mv_builder.with_training_data(self.training_data) 

        collected_meta = CollectedMetadata.collect(cwd).to_metadata()
        if self.metadata:
            collected_meta.update(self.metadata)
        mv_builder.with_metadata(collected_meta)

        if self.monitoring_configuration:
            mc = SDK_MC(self.monitoring_configuration.batch_size)
            mv_builder.with_monitoring_configuration(mc)

        logging.debug(f"Model version builder:\n{mv_builder}")

        mv = mv_builder.build(conn)
        build_log_handler = DockerLogHandler()
        logging.info("Build logs:")
        for ev in mv.build_logs():
            build_log_handler.show(ev.data)

        if self.monitoring:
            logging.info(f"Uploading monitoring configuration for the model {mv.name}:{mv.version}")
            for mon in self.monitoring:  
                name, version = mon.config.monitoring_model.split(":")
                mon_mv = SDK_MV.find(conn, name, int(version))
                sdk_conf = MetricSpecConfig(
                    modelversion_id = mon_mv.id,
                    threshold = mon.config.threshold,
                    threshold_op = mon.config.operator
                )
                sdk_ms = MetricSpec.create(
                    cluster = conn,
                    name = mon.name,
                    modelversion_id = mv.id,
                    config = sdk_conf
                )
                logging.debug(f"Created metric spec: {sdk_ms.name} with id {sdk_ms.id}")

        return mv