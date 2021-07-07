from hydrosdk.cluster import Cluster
import pytest
import pathlib

import yaml
from hs.entities.deployment_config import DeploymentConfig

@pytest.fixture()
def dep_conf_path():
    return pathlib.Path("./tests/resources/deployment_configuration.yaml")

def test_depconf_parse(dep_conf_path: pathlib.Path):
    with open(dep_conf_path, "r") as f:
        obj = yaml.safe_load(f)
    dc: DeploymentConfig = DeploymentConfig.parse_obj(obj)
    print(dc)

def test_depconf_apply(dep_conf_path):
    conn = Cluster("http://")
    with open(dep_conf_path, "r") as f:
        obj = yaml.safe_load(f)
    dc: DeploymentConfig = DeploymentConfig.parse_obj(obj)
    dc.apply(conn)