from hydroserving.httpclient.api import *
from hydroserving.httpclient.remote_connection import RemoteConnection


class HydroservingClient:
    def __init__(self, remote_addr):
        self.connection = RemoteConnection(remote_addr)
        self.models = ModelAPI(self.connection)
        self.runtimes = RuntimeAPI(self.connection)
        self.applications = ApplicationAPI(self.connection)
        self.sources = SourceAPI(self.connection)
