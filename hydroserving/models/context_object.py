class ContextObject:
    def __init__(self, metadata=None, docker_client=None, kafka_params=None, app_data=None):
        self.metadata = metadata
        self.docker_client = docker_client
        self.kafka_params = kafka_params
        self.app_data = app_data
