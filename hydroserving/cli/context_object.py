from hydroserving.config.config import ConfigService

from hydroserving.core.apply import ApplyService
from hydroserving.core.application.service import ApplicationService
from hydroserving.core.host_selector.host_selector import HostSelectorService
from hydroserving.core.model.service import ModelService
from hydroserving.core.monitoring.service import MonitoringService


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

        self.apply_service = ApplyService(
            self.model_service,
            self.selector_service,
            self.application_service,
        )

    @staticmethod
    def with_config_path(path, overridden_cluster=None):
        """
        Instantiates base services.
        Args:
            overridden_cluster:
            path (str): path to home folder

        Returns:
            ContextServices
        """
        config_service = ConfigService(path, overridden_cluster=overridden_cluster)
        if overridden_cluster and config_service.current_cluster() is None:
            raise ValueError("No cluster definition for '{}' cluster".format(overridden_cluster))
        return ContextObject(config=config_service)
