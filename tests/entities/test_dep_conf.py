import json
from hydrosdk.cluster import Cluster
import pytest
import pathlib
from requests.models import Response

import yaml
from hs.entities.deployment_config import DeploymentConfig
from unittest.mock import patch


@pytest.fixture()
def dep_conf_path():
    return pathlib.Path("./tests/resources/deployment_configuration.yaml")

def test_depconf_parse(dep_conf_path: pathlib.Path):
    with open(dep_conf_path, "r") as f:
        obj = yaml.safe_load(f)
    dc: DeploymentConfig = DeploymentConfig.parse_obj(obj)
    print(dc)


@patch('hydrosdk.cluster.Cluster.request')
def test_depconf_apply(mock_request, dep_conf_path):
    resp = Response()
    resp.status_code = 200
    resp._content = json.dumps({"name": "test"}).encode("utf-8")
    mock_request.return_value = resp
    conn = Cluster("http://")
    with open(dep_conf_path, "r") as f:
        obj = yaml.safe_load(f)
    dc: DeploymentConfig = DeploymentConfig.parse_obj(obj)
    dc.apply(conn)