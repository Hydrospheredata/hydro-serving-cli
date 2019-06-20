import json

from hydroserving.core.model.entities import UploadMetadata
from hydroserving.core.model.package import assemble_model, enrich_and_normalize
from hydroserving.core.model.upload import upload_model


class ModelService:
    def __init__(self, connection, monitoring_service):
        """

        Args:
            connection (RemoteConnection):
        """
        self.connection = connection
        self.monitoring_service = monitoring_service

    def get_logs(self, model_version_id):
        return self.connection.sse("/api/v2/model/version/{}/logs".format(model_version_id))

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
        return None

    def find_model(self, model_name):
        """

        Args:
            model_name:
        Returns:

        """
        models = self.list_models()
        if models:
            for m in models:
                if m['name'] == model_name:
                    return m
        return None

    def apply(self, model, path, no_training_data=False, ignore_monitoring=False):
        """

        Args:
            ignore_monitoring (bool):
            no_training_data (bool):
            model (Model):
            path (str): where to build

        Returns:

        """
        model = enrich_and_normalize(path, model)
        tar = assemble_model(model, path)
        result = upload_model(
            model_service=self,
            monitoring_service=self.monitoring_service,
            model=model,
            model_path=tar,
            is_async=False,
            ignore_training_data=no_training_data,
            ignore_monitoring=ignore_monitoring
        )
        return result

    def delete(self, model_id):
        res = self.connection.delete("/api/v2/model/{}".format(model_id))
        if res.ok:
            return res.json()
        return None
