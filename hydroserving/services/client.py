from hydroserving.httpclient.client import RemoteConnection
from hydroserving.services.config import ConfigService


class HttpService:
    def __init__(self, config_service):
        """

        Args:
            config_service (ConfigService):
        """
        self.config_service = config_service

    def get(self, url):
        return self.connection().get(url)

    def post(self, url, data):
        return self.connection().post(url, data)

    def multipart_post(self, url, data, files, create_encoder_callback=None):
        return self.connection().multipart_post(url, data, files, create_encoder_callback)

    def connection(self):
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
