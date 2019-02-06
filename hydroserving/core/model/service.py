import json
from hydroserving.core.model.entities import UploadMetadata
from hydroserving.core.model.package import assemble_model
from hydroserving.core.model.upload import upload_model
from hydroserving.http.remote_connection import RemoteConnection


class InvalidModelException(RuntimeError):
    def __init__(self, msg, model_dict):
        super().__init__(msg)
        self.model_dict = model_dict


class ModelService:
    def __init__(self, connection, profiler_service):
        """

        Args:
            connection (RemoteConnection):
        """
        self.connection = connection
        self.profiler_service = profiler_service

    def list_models(self):
        """

        Returns:

        """
        return self.connection.get("/api/v2/model").json()

    def upload(self, assembly_path, metadata):
        """

        Args:
            assembly_path:
            metadata:

        Returns:

        """
        if not isinstance(metadata, UploadMetadata):
            raise TypeError("{} is not UploadMetadata".format(metadata), type(metadata))
        result = self.connection.multipart_post(
            url="/api/v2/model/upload",
            data={"metadata": json.dumps(metadata.__dict__)},
            files={"payload": ("filename", open(assembly_path, "rb"))}
        )
        if result.ok:
            return result.json()
        else:
            raise ValueError("Invalid request: {}".format(result.content.decode("utf-8")))

    def list_versions(self):
        """

        Returns:

        """
        return self.connection.get("/api/v2/model/version").json()

    def find_version(self, model_name, model_version):
        """

        Args:
            model_name:
            model_version:

        Returns:

        """
        res = self.connection.get("/api/v2/model/version/{}/{}".format(model_name, model_version))
        if res.ok:
            return res.json()
        else:
            return None

    def apply(self, model, path):
        """

        Args:
            model (Model):
            path (str): where to build

        Returns:

        """
        tar = assemble_model(model, path)
        result = upload_model(self, self.profiler_service, model, tar, is_async=False)
        return result
