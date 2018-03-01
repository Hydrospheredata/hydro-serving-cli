import os
import yaml

from hydroserving.models.deployment import LocalDeployment
from hydroserving.models.model_definition import ModelDefinition


class FolderMetadata:
    def __init__(self, model, local_deployment):
        self.model = model
        self.local_deployment = local_deployment

    @staticmethod
    def from_dict(data_dict):
        if data_dict is None:
            return None

        model_dict = data_dict.get("model")
        runtime_dict = data_dict.get("local_deploy")
        return FolderMetadata(
            model=ModelDefinition.from_dict(model_dict),
            local_deployment=LocalDeployment.from_dict(runtime_dict)
        )

    @staticmethod
    def from_directory(directory_path):
        if not os.path.exists(directory_path):
            raise FileNotFoundError("{} doesn't exist".format(directory_path))
        if not os.path.isdir(directory_path):
            raise NotADirectoryError("{} is not a directory".format(directory_path))

        metafile = os.path.join(directory_path, "serving.yaml")
        if not os.path.exists(metafile):
            return None

        with open(metafile, "r") as serving_file:
            return FolderMetadata.from_dict(yaml.load(serving_file.read()))
