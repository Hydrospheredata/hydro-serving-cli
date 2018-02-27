import os
import yaml
from hydroserving.models.metadata import Metadata


def read_metadata(directory_path):
    if not os.path.exists(directory_path):
        raise FileNotFoundError("{} doesn't exist".format(directory_path))
    if not os.path.isdir(directory_path):
        raise NotADirectoryError("{} is not a directory".format(directory_path))

    metafile = os.path.join(directory_path, "serving.yaml")
    if not os.path.exists(metafile):
        return None

    with open(metafile, "r") as serving_file:
        return Metadata.from_dict(yaml.load(serving_file.read()))
