from hydroserving.httpclient.api import ModelAPI, RuntimeAPI, ApplicationAPI, SourceAPI
from hydroserving.httpclient.remote_connection import RemoteConnection


class HydroservingClient:
    def __init__(self, addr):
        if isinstance(addr, str):
            self.connection = RemoteConnection(addr)
        else:
            raise TypeError("{} is not a string".format(addr))

        self.models = ModelAPI(self.connection)
        self.runtimes = RuntimeAPI(self.connection)
        self.applications = ApplicationAPI(self.connection)
        self.sources = SourceAPI(self.connection)
