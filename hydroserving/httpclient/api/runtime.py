class RuntimeAPI:
    def __init__(self, connection):
        self.connection = connection

    def create(self, name, version, rtypes, tags=None, config_params=None):
        if config_params is None:
            config_params = {}
        if tags is None:
            tags = []
        data = {
            "name": name,
            "version": version,
            "modelTypes": rtypes,
            "tags": tags,
            "configParams": config_params
        }
        return self.connection.post("/api/v1/runtime", data)

    def list(self):
        return self.connection.get("/api/v1/runtime")

    def find(self, name, version):
        for runtime in self.list():
            if runtime["name"] == name and runtime["version"] == version:
                return runtime
        return None
