from hydroserving.models.runtime import Runtime


class LocalDeployment:
    def __init__(self, name, runtime, port, build):
        self.name = name
        self.runtime = runtime
        self.port = port
        self.build = build

    @staticmethod
    def from_dict(data_dict):
        if data_dict is None:
            return None
        return LocalDeployment(
            name=data_dict.get("name"),
            runtime=Runtime.from_dict(data_dict.get("runtime")),
            port=data_dict.get("port"),
            build=data_dict.get("build")
        )
