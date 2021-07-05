import pytest
import pathlib
import os

from hs.entities.model_version import ModelVersion

@pytest.fixture()
def model_yaml_path():
    return pathlib.Path("./examples/full-apply-example/3-claims-model.yml")

def test_model_deserialize(model_yaml_path):
    model_version = ModelVersion.parse_file(model_yaml_path)
    print(model_version)
    #todo: implement assertions. they are better than manual check 👀