import logging
import json


class HostSelector:
    def __init__(self, name, node_selector):
        """

        Args:
            name (str): name of environment
            selector (str): map-like node selector (kubernetes-specific)
        """
        self.name = name
        self.node_selector = node_selector


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

    def delete(self, env_name):
        return self.connection.delete("/api/v2/hostSelector/{}".format(env_name)).json()

    def create(self, env_name, node_selector):
        data = {
            'name': env_name,
            'nodeSelector': node_selector
        }
        response = self.connection.post_json("/api/v2/hostSelector", data)
        try:
            if not response.ok:
                raise RuntimeError("")
            return response.json()
        except:
            logging.error("Cannot create Host Selector: %s" % (response.text, ))
            raise SystemExit(-1)

    def apply(self, env):
        found_env = self.get(env.name)
        if found_env is not None:
            logging.warning("%s environment already exists", env.name)
            return None
        return self.create(env.name, env.node_selector)
