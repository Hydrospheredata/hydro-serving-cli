from hydroserving.httpclient.errors import HSApiError


class UploadMetadata:
    def __init__(self, model_name, model_type, target_source, model_contract, description):
        self.model_description = description
        self.model_contract = model_contract
        self.target_source = target_source
        self.model_type = model_type
        self.model_name = model_name


class ModelAPI:
    def __init__(self, connection):
        self.connection = connection

    def build(self, model_id):
        data = {
            "modelId": model_id
        }
        return self.connection.post("/api/v1/model/build", data)

    def list(self):
        return self.connection.get("/api/v1/model")

    def upload(self, assembly_path, metadata):
        if not isinstance(metadata, UploadMetadata):
            raise HSApiError("{} is not UploadMetadata".format(metadata))

        return self.connection.multipart_post(
            "/api/v1/model",
            metadata.__dict__,
            {"payload": open(assembly_path, "rb")}
        )

    def list_versions(self):
        return self.connection.get("/api/v1/model/version")

    def find_version(self, model_name, model_version):
        for version in self.list_versions():
            if version["modelName"] == model_name and version["modelVersion"] == model_version:
                return version
        return None
