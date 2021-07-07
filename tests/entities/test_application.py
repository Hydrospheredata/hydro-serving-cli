from hs.entities.application import Application
from hydro_serving_grpc.serving.contract.signature_pb2 import ModelSignature
from hydrosdk.cluster import Cluster
from hydrosdk.image import DockerImage
from hydrosdk.modelversion import ModelVersion
from hydrosdk.exceptions import HydrosphereException
from hydrosdk.application import Application as HS_APP, ExecutionGraph
import pytest
import pathlib
from unittest.mock import patch

@pytest.fixture()
def singular_yaml_path():
    return pathlib.Path("./examples/full-apply-example/4-claims-app.yml")

@pytest.fixture()
def pipeline_yaml_path():
    return pathlib.Path("./examples/full-apply-example/5-claims-pipeline-app.yml")


def test_singular_parse(singular_yaml_path):
    app = Application.parse_file(singular_yaml_path)
    print(app)

def test_pipeline_parse(pipeline_yaml_path):
    app = Application.parse_file(pipeline_yaml_path)
    print(app)

@patch('hydrosdk.modelversion.ModelVersion.find')
@patch('hydrosdk.application.Application.find')
@patch('hydrosdk.application.ApplicationBuilder.build')
def test_singluar_apply(mock_app_build, mock_app_find, mock_mv_find, singular_yaml_path):
    conn = Cluster("http://")
    mock_mv_find.return_value = ModelVersion(
        cluster=conn,
        id = 1,
        model_id=1,
        name="claims-model",
        version=1,
        signature=ModelSignature(),
        status="Released",
        image=DockerImage(name = "aaa", tag = "aaa"),
        runtime=DockerImage(name = "aaa", tag = "aaa"),
        is_external=False
    )
    mock_app_find.side_effect = HydrosphereException()
    mock_app_build.return_value = HS_APP(
        cluster=conn,
        id=1,
        name="app",
        execution_graph=ExecutionGraph([]),
        status="Ready",
        signature=ModelSignature(),
        kafka_streaming=[]
    )
    app: Application = Application.parse_file(singular_yaml_path)
    app.apply(conn)

@patch('hydrosdk.modelversion.ModelVersion.find')
@patch('hydrosdk.application.Application.find')
@patch('hydrosdk.application.ApplicationBuilder.build')
def test_pipeline_apply(mock_app_build, mock_app_find, mock_mv_find, pipeline_yaml_path):
    conn = Cluster("http://")
    mock_mv_find.return_value = ModelVersion(
        cluster=conn,
        id = 1,
        model_id=1,
        name="claims-model",
        version=1,
        signature=ModelSignature(),
        status="Released",
        image=DockerImage(name = "aaa", tag = "aaa"),
        runtime=DockerImage(name = "aaa", tag = "aaa"),
        is_external=False
    )
    mock_app_find.side_effect = HydrosphereException()
    mock_app_build.return_value = HS_APP(
        cluster=conn,
        id=1,
        name="app",
        execution_graph=ExecutionGraph([]),
        status="Ready",
        signature=ModelSignature(),
        kafka_streaming=[]
    )
    app: Application = Application.parse_file(singular_yaml_path)
    app.apply(conn)

@patch('hydrosdk.modelversion.ModelVersion.find')
@patch('hydrosdk.application.Application.find')
@patch('hydrosdk.application.Application.delete')
@patch('hydrosdk.application.ApplicationBuilder.build')
def test_pipeline_apply(mock_app_build, mock_app_delete, mock_app_find, mock_mv_find, singular_yaml_path):
    conn = Cluster("http://")
    mock_mv_find.return_value = ModelVersion(
        cluster=conn,
        id = 1,
        model_id=1,
        name="claims-model",
        version=1,
        signature=ModelSignature(),
        status="Released",
        image=DockerImage(name = "aaa", tag = "aaa"),
        runtime=DockerImage(name = "aaa", tag = "aaa"),
        is_external=False
    )
    mock_app_find.return_value = HS_APP(
        cluster=conn,
        id=1,
        name="app",
        execution_graph=ExecutionGraph([]),
        status="Ready",
        signature=ModelSignature(),
        kafka_streaming=[]
    )
    mock_app_build.return_value = HS_APP(
        cluster=conn,
        id=1,
        name="app",
        execution_graph=ExecutionGraph([]),
        status="Ready",
        signature=ModelSignature(),
        kafka_streaming=[]
    )
    app: Application = Application.parse_file(singular_yaml_path)
    app.apply(conn)