from hydroserving.models.definitions.config import Config
from hydroserving.services.config import ConfigService
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
    def __init__(self, config):
        """

        :param config:
        :type config: ConfigService
        """
        self.config = config
