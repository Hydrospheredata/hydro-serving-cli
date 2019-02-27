import logging


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
        resp = self.connection.get("/api/v2/hostSelector/{}".format(env_name))
        if resp.ok:
            return resp.json()
        return None

    def list(self):
        return self.connection.get("/api/v2/hostSelector").json()

    def create(self, env_name, env_selector):
        data = {
            'name': env_name,
            'placeholders': [env_selector]
        }
        return self.connection.post_json("/api/v2/hostSelector", data).json()

    def apply(self, env):
        found_env = self.get(env.name)
        if found_env is not None:
            logging.warning("%s environment already exists", env.name)
            return None
        return self.create(env.name, env.selector)
