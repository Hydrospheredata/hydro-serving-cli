from hydro_serving_grpc import ModelContract
import json
from hydroserving.http.remote_connection import RemoteConnection


class Model:
    def __init__(self, name, host_selector, runtime, contract, payload,
                 training_data_file, install_command):
        """
        Args:
            name (str):
            contract (ModelContract or None):
            payload (list of str):
            training_data_file (str or None):
        """
        if not isinstance(name, str):
            raise TypeError("name is not a string", type(name))

        if runtime is None:
            raise ValueError("runtime cannot be None")

        if contract is not None and not isinstance(contract, ModelContract):
            raise TypeError("contract is not a ModelContract", type(contract))

        if not isinstance(payload, list):
            raise TypeError("payload is not a list", type(contract))

        if install_command is not None and not isinstance(install_command, str):
            raise TypeError("install-command is not a string", type(install_command))

        self.name = name
        self.host_selector = host_selector
        self.runtime = runtime
        self.contract = contract
        self.payload = payload
        self.training_data_file = training_data_file
        self.install_command = install_command


class UploadMetadata:
    def __init__(self, name, contract, host_selector, runtime, install_command):
        self.contract = contract
        self.hostSelectorName = host_selector
        self.runtime = runtime
        self.name = name
        self.installCommand = install_command


class ModelService:
    def __init__(self, connection):
        """

        Args:
            connection (RemoteConnection):
        """
        self.connection = connection

    def list_models(self):
        """

        Returns:

        """
        return self.connection.get("/api/v2/model").json()

    def upload(self, assembly_path, metadata, create_encoder_callback=None):
        """

        Args:
            assembly_path:
            metadata:
            create_encoder_callback:

        Returns:

        """
        if not isinstance(metadata, UploadMetadata):
            raise TypeError("{} is not UploadMetadata".format(metadata), type(metadata))
        result = self.connection.multipart_post(
            url="/api/v2/model/upload",
            data={"metadata": json.dumps(metadata.__dict__)},
            files={"payload": ("filename", open(assembly_path, "rb"))},
            create_encoder_callback=create_encoder_callback
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
