from hydroserving.config.config import ConfigService

from hydroserving.core.apply import ApplyService
from hydroserving.core.model.model import ModelService
from hydroserving.core.host_selector import HostSelectorService
from hydroserving.core.application import ApplicationService
from hydroserving.core.profiler import ProfilerService


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
        self.profiler_service = ProfilerService(conn)
        self.apply_service = ApplyService(
            self.model_service,
            self.selector_service,
            self.application_service,
            self.profiler_service
        )

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
        return ContextObject(config=config_service)
