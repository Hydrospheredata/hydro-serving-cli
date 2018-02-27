class Model:
    def __init__(self, name, model_type, contract_path, payload):
        self.name = name
        self.model_type = model_type
        self.contract_path = contract_path
        self.payload = payload

    @staticmethod
    def from_dict(data_dict):
        if data_dict is None:
            return None
        return Model(
            name=data_dict.get("name"),
            model_type=data_dict.get("type"),
            contract_path=data_dict.get("contract"),
            payload=data_dict.get("payload")
        )


class Runtime:
    def __init__(self, repository, tag):
        self.repository = repository
        self.tag = "latest" if tag is None else tag

    def __str__(self):
        return "{}:{}".format(self.repository, self.tag)

    @staticmethod
    def from_dict(data_dict):
        if data_dict is None:
            return None
        return Runtime(
            repository=data_dict.get("repository"),
            tag=data_dict.get("tag")
        )


class LocalDeployment:
    def __init__(self, name, runtime, port):
        self.name = name
        self.runtime = runtime
        self.port = port

    @staticmethod
    def from_dict(data_dict):
        if data_dict is None:
            return None
        return LocalDeployment(
            name=data_dict.get("name"),
            runtime=Runtime.from_dict(data_dict.get("runtime")),
            port=data_dict.get("port")
        )


class Metadata:
    def __init__(self, model, local_deployment):
        self.model = model
        self.local_deployment = local_deployment

    @staticmethod
    def from_dict(data_dict):
        if data_dict is None:
            return None

        model_dict = data_dict.get("model")
        runtime_dict = data_dict.get("local_deploy")
        return Metadata(
            model=Model.from_dict(model_dict),
            local_deployment=LocalDeployment.from_dict(runtime_dict)
        )
