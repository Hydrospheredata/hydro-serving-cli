class ContextObject:
    def __init__(self, config=None, metadata=None, kafka_params=None, services=None):
        self.metadata = metadata
        self.kafka_params = kafka_params
        self.config = config
        self.services = services


class ContextServices:
    def __init__(self, config):
        self.config = config
