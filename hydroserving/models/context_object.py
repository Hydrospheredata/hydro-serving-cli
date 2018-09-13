from hydroserving.models.definitions.config import Config
from hydroserving.services.config import ConfigService
from hydroserving.services.client import HttpService
from hydroserving.models.kafka_params import KafkaParams


class ContextObject:
    def __init__(self, config=None, kafka_params=None, services=None, **kwargs):
        """
        :param config:
        :type config: Config
        :param kafka_params:
        :type kafka_params: KafkaParams
        :param services:
        :type services: ContextServices
        """
        self.kafka_params = kafka_params
        self.config = config
        self.services = services
        self.misc = kwargs


class ContextServices:
    def __init__(self, config, http):
        """

        Args:
            config (ConfigService):
            http (HttpService):
        """
        self.config = config
        self.http = http

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
        http_service = HttpService(config_service)
        return ContextServices(
            config=config_service,
            http=http_service
        )
