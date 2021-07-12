import pytest
import pathlib
from hydrosdk.cluster import Cluster

from hs.entities.model_version import ModelVersion

from unittest.mock import patch

@pytest.fixture()
def model_yaml_path():
    return pathlib.Path("./examples/full-apply-example/3-claims-model.yml")


def test_model_parse(model_yaml_path):
    model_version = ModelVersion.parse_file(model_yaml_path)
    print(model_version)
    #todo: implement assertions. they are better than manual check 👀

@patch('hydrosdk.monitoring.MetricSpec.create')
@patch('hydrosdk.modelversion.ModelVersion.find')
@patch('hydrosdk.modelversion.ModelVersionBuilder.build')
def test_model_apply(mock_builder, mock_find, mock_metric_create, model_yaml_path):
    conn = Cluster("http://")

    model_version = ModelVersion.parse_file(model_yaml_path)
    model_version.apply(conn, "./examples/full-apply-example/")
