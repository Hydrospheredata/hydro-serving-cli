class HostSelector:
    def __init__(self, name, selector):
        """

        Args:
            name (str): name of environment
            selector (str): json-like env selector
        """
        self.name = name
        self.selector = selector

class HostSelectorService:
    def __init__(self, connection):
        """

        Args:
            connection (RemoteConnection):
        """
        self.connection = connection

    def get(self, env_name):
        for env in self.list():
            if env['name'] == env_name:
                return env
        return None

    def list(self):
        return self.connection.get("/api/v1/environment")

    def create(self, env_name, env_selector):
        data = {
            'name': env_name,
            'placeholders': [env_selector]
        }
        return self.connection.post("/api/v1/environment", data)
