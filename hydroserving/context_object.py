class ContextObject:
    def __init__(self, metadata=None, docker_client=None):
        self.metadata = metadata
        self.docker_client = docker_client
