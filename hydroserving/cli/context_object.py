import logging
import os

from hydrosdk.cluster import Cluster 

from hydroserving.config import ConfigService
from hydroserving.config.settings import HOME_PATH_EXPANDED
from hydroserving.core.application.service import ApplicationService
from hydroserving.core.apply import ApplyService
from hydroserving.core.deployment_config.service import DeploymentConfigurationService
from hydroserving.core.model.service import ModelService
from hydroserving.core.monitoring.service import MonitoringService
from hydroserving.core.servable.service import ServableService
from hydroserving.errors.config import ClusterNotFoundError


class ContextObject:

    def __init__(self, config_service: ConfigService):
        self.config_service = config_service
        self.cluster = None
        try:
            cluster_definition = config_service.current_cluster()
            self.cluster = Cluster(cluster_definition.get('cluster', {}).get('server', 'unknown'))
        except ClusterNotFoundError:
            logging.debug("Current cluster is unset, initializing without cluster endpoint")
        self.model_service = ModelService(self.cluster)
        self.application_service = ApplicationService(self.cluster)
        self.servable_service = ServableService(self.cluster)
        self.deployment_configuration_service = DeploymentConfigurationService(self.cluster)
        self.apply_service = ApplyService(
            self.model_service,
            self.application_service,
            self.deployment_configuration_service
        )

    @staticmethod
    def with_config_path(path=HOME_PATH_EXPANDED, overridden_cluster=None):
        """
        Instantiates base services.
        Args:
            overridden_cluster:
            path (str): path to home folder

        Returns:
            ContextServices
        """
        if not os.path.isdir(HOME_PATH_EXPANDED):
            logging.debug("Didn't find {} folder, creating".format(HOME_PATH_EXPANDED))
            os.mkdir(HOME_PATH_EXPANDED)
        config_service = ConfigService(path, overridden_cluster=overridden_cluster)
        try:
            _ = overridden_cluster is not None and config_service.current_cluster()
        except ClusterNotFoundError as e:
            logging.error(f"No cluster definition for '{overridden_cluster}'")
            raise SystemExit(1)
        return ContextObject(config_service=config_service)
