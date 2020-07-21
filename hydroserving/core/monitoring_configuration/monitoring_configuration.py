import logging


class MonitoringConfiguration:
    def __init__(self, batch_size):
        """

        Args:
            batch_size(str): size of the batch
        """
        self.batch_size = batch_size


class MonitoringConfigurationService:
    def __init__(self, connection):
        """

        Args:
            connection (RemoteConnection):
        """
        self.connection = connection

    def get(self, env_name):
        resp = self.connection.get("/api/v2/monitoringConfiguration/{}".format(env_name))
        if resp.ok:
            return resp.json()
        return None

    def list(self):
        return self.connection.get("/api/v2/monitoringConfiguration").json()

    def create(self, batch_size):
        data = {
            'batch_size': batch_size
        }
        return self.connection.post_json("/api/v2/monitoringConfiguration", data).json()

    def apply(self, env):
        found_env = self.get(env.batch_size)
        if found_env is not None:
            logging.warning("%s environment already exists", env.name)
            return None
        return self.create(env.batch_size)
