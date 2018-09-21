from hydroserving.httpclient.errors import HSApiError


class UploadMetadata:
    def __init__(self, model_name, model_type, model_contract, description):
        self.model_description = description
        self.model_contract = model_contract
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

    def build_status(self, build_id):
        """

        Args:
            build_id (str):
        """
        return self.connection.get("/api/v1/model/build/" + build_id)

    def list(self):
        return self.connection.get("/api/v1/model")

    def upload(self, assembly_path, metadata, create_encoder_callback=None):
        if not isinstance(metadata, UploadMetadata):
            raise HSApiError("{} is not UploadMetadata".format(metadata))
        return self.connection.multipart_post(
            url="/api/v1/model/upload",
            data=metadata,
            files={"payload": ("filename", open(assembly_path, "rb"))},
            create_encoder_callback=create_encoder_callback
        )

    def list_versions(self):
        return self.connection.get("/api/v1/model/version")

    def find_version(self, model_name, model_version):
        for version in self.list_versions():
            if version["modelName"] == model_name and version["modelVersion"] == model_version:
                return version
        return None
