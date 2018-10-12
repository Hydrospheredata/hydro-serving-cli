from hydroserving.httpclient.api import ApplicationAPI, ModelAPI, RuntimeAPI
from hydroserving.httpclient.api.environment import EnvironmentAPI
from hydroserving.httpclient.api.monitoring import MonitoringAPI
from hydroserving.httpclient.client import RemoteConnection
from hydroserving.services.config import ConfigService


class HttpService:
    def __init__(self, config_service):
        """

        Args:
            config_service (ConfigService):
        """
        self.config_service = config_service
        self.connection = self.get_connection()

    def get(self, url):
        return self.connection.get(url)

    def post(self, url, data):
        return self.connection.post(url, data)

    def multipart_post(self, url, data, files, create_encoder_callback=None):
        return self.connection.multipart_post(url, data, files, create_encoder_callback)

    def app_api(self):
        return ApplicationAPI(self.connection)

    def model_api(self):
        return ModelAPI(self.connection)

    def profiler_api(self):
        return ModelAPI(self.connection)

    def env_api(self):
        return EnvironmentAPI(self.connection)

    def runtime_api(self):
        return RuntimeAPI(self.connection)

    def monitoring_api(self):
        return MonitoringAPI(self.connection)

    def get_connection(self):
        """

        Returns :
            RemoteConnection: if there is current cluster
            None: otherwise
        """
        current_cluster = self.config_service.current_cluster()
        if current_cluster is not None:
            return RemoteConnection(current_cluster['cluster']['server'])
        else:
            return None
