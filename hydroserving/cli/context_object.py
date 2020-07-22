import os
import logging
from hydroserving.config.config import ConfigService
from hydroserving.core.apply import ApplyService
from hydroserving.core.application.service import ApplicationService
from hydroserving.core.monitoring_configuration.monitoring_configuration import MonitoringConfigurationService
from hydroserving.core.host_selector.host_selector import HostSelectorService
from hydroserving.core.model.service import ModelService
from hydroserving.core.monitoring.service import MonitoringService
from hydroserving.config.settings import HOME_PATH_EXPANDED
from hydroserving.core.servable.service import ServableService


class ContextObject:

    def __init__(self, config):
        """

        Args:
            config (ConfigService):
        """
        self.config_service = config
        conn = config.get_connection()
        self.monitoring_service = MonitoringService(conn)
        self.model_service = ModelService(conn, self.monitoring_service)
        self.selector_service = HostSelectorService(conn)
        self.application_service = ApplicationService(conn, self.model_service)
        self.mc_service = MonitoringConfigurationService(conn)
        self.servable_service = ServableService(conn)

        self.apply_service = ApplyService(
            self.model_service,
            self.selector_service,
            self.application_service,
            self.mc_service
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
            logging.debug("Didn't find {} folder. Creating...".format(HOME_PATH_EXPANDED))
            os.mkdir(HOME_PATH_EXPANDED)
        config_service = ConfigService(path, overridden_cluster=overridden_cluster)
        if overridden_cluster and config_service.current_cluster() is None:
            raise ValueError("No cluster definition for '{}' cluster".format(overridden_cluster))
        return ContextObject(config=config_service)
