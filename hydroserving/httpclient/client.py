from hydroserving.httpclient.api import *
from hydroserving.httpclient.remote_connection import RemoteConnection


class HydroservingClient:
    def __init__(self, addr_or_connection):
        if isinstance(addr_or_connection, RemoteConnection):
            self.connection = addr_or_connection
        elif isinstance(addr_or_connection, str):
            self.connection = RemoteConnection(addr_or_connection)
        else:
            raise TypeError("{} is neither a RemoteConnection nor a string".format(addr_or_connection))

        self.models = ModelAPI(self.connection)
        self.runtimes = RuntimeAPI(self.connection)
        self.applications = ApplicationAPI(self.connection)
        self.sources = SourceAPI(self.connection)
