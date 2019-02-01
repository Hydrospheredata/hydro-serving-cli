from hydroserving.config.config import ClusterConfig
from hydroserving.core.services.config import ConfigService

from hydroserving.core.model.model import ModelService
from hydroserving.core.host_selector import HostSelectorService
from hydroserving.core.application import ApplicationService


class ContextObject:
    def __init__(self, config):
        """

        Args:
            config (ConfigService):
        """
        self.config_service = config
        conn = config.get_connection()
        self.model_service = ModelService(conn)
        self.selector_service = HostSelectorService(conn)
        self.application_service = ApplicationService(conn)

    @staticmethod
    def with_config_path(path):
        """
        Instantiates base services.
        Args:
            path (str): path to home folder

        Returns:
            ContextServices
        """
        config_service = ConfigService(path)
        return ContextServices(
            config=config_service
        )