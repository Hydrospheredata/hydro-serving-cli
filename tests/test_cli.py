import json
import tempfile
from tests.testutils import mock_sse_response
import pytest
import requests
import requests_mock
import logging
from click.testing import CliRunner

from hs.cli.commands import hs_cli
from hs.entities.cluster_config import ClusterConfig, ClusterDef, ClusterServerDef

logging.root.setLevel(logging.DEBUG)

@pytest.yield_fixture(scope="module")
def cluster_config():
    with tempfile.NamedTemporaryFile("w+", suffix=".yaml") as f:
        print(f"Created temporary config file {f.name}")
        config = ClusterConfig(
            current_cluster = "test",
            clusters = [
                ClusterDef(
                    name = "test",
                    cluster = ClusterServerDef(server = "http://localhost")
                )
            ]
        )
        f.write(config.to_yaml())
        f.seek(0)
        yield f.name


def test_hs():
    runner = CliRunner()
    result = runner.invoke(hs_cli, [])
    print(result)
    assert result.exit_code == 0

def test_model_apply(cluster_config: str):
    def _upload_matcher(request):
        resp = None
        if request.path_url == "/api/v2/model/upload":
            resp = requests.Response()
            resp.status_code = 200
            resp._content = json.dumps(
                {
                    "id": 1,
                    "model": {"name": "apply-demo-claims-model", "id": 1},
                    "modelVersion": 1,
                    "status": "Assembling",
                    "modelSignature": {
                        "signatureName": "predict",
                        "inputs": [],
                        "outputs": []
                    },
                    "monitoringConfiguration": {
                        "batchSize": 100
                    },
                    "runtime": {
                        "name": "python",
                        "tag": "latest"
                    },
                    "metadata": {}
                }
            ).encode("utf-8")
        elif request.path_url == '/api/v2/model/version/apply-demo-claims-model/1':
            resp = requests.Response()
            resp.status_code = 200
            resp._content = json.dumps(
                {
                    "id": 1,
                    "model": {"name": "apply-demo-claims-model", "id": 1},
                    "modelVersion": 1,
                    "status": "Released",
                    "modelSignature": {
                        "signatureName": "predict",
                        "inputs": [],
                        "outputs": []
                    },
                    "monitoringConfiguration": {
                        "batchSize": 100
                    },
                    "runtime": {
                        "name": "python",
                        "tag": "latest"
                    },
                    "metadata": {}
                }
            ).encode("utf-8")
        elif request.path_url == '/api/v2/model/version/apply-demo-claims-autoencoder/1':
            resp = requests.Response()
            resp.status_code = 200
            resp._content = json.dumps(
                {
                    "id": 1337,
                    "model": {"name": "apply-demo-claims-autoencoder", "id": 2},
                    "modelVersion": 1,
                    "status": "Released",
                    "modelSignature": {
                        "signatureName": "predict",
                        "inputs": [],
                        "outputs": []
                    },
                    "monitoringConfiguration": {
                        "batchSize": 100
                    },
                    "runtime": {
                        "name": "python",
                        "tag": "latest"
                    },
                    "metadata": {}
                }
            ).encode("utf-8")
        elif request.path_url == "/api/v2/monitoring/metricspec" and request.method == "POST":
            print(request.json())
            resp = requests.Response()
            resp.status_code = 200
            resp._content = json.dumps(
                {
                    'name': 'cool-metric', 
                    'modelVersionId': 1, 
                    'config': {
                        'modelVersionId': 1337, 
                        'threshold': 12.0, 
                        'thresholdCmpOperator': {'kind': '<='}
                    },
                    "id": "aaa"
                }
            ).encode("utf-8")
        elif request.path_url == '/api/v2/model/version/1/logs':
            resp = mock_sse_response("data: Hello there".encode("utf-8"))
        elif request.path_url == '/monitoring/profiles/batch/1/s3':
            resp = requests.Response()
            resp._content = "".encode("utf-8")
            resp.status_code = 200
        return resp

    with requests_mock.Mocker() as req_mock:
        req_mock.add_matcher(_upload_matcher)
        runner = CliRunner()
        result = runner.invoke(hs_cli, ["-v", "--config-file", cluster_config, "apply", "-f", "./examples/full-apply-example/3-claims-model.yml"], catch_exceptions=False)
        print(result.output)
        assert result.exit_code == 0

def test_application_singular_apply(cluster_config):
    t = 1
    def _upload_matcher(request):
        resp = None
        if request.path_url == "/api/v2/model/version/apply-demo-claims-model/2":
            resp = requests.Response()
            resp.status_code = 200
            resp._content = json.dumps(
                {
                    "id": 1,
                    "model": {"name": "apply-demo-claims-model", "id": 1},
                    "modelVersion": 1,
                    "status": "Released",
                    "modelSignature": {
                        "signatureName": "predict",
                        "inputs": [],
                        "outputs": []
                    },
                    "monitoringConfiguration": {
                        "batchSize": 100
                    },
                    "runtime": {
                        "name": "python",
                        "tag": "latest"
                    },
                    "metadata": {}
                }
            ).encode("utf-8")
        elif request.path_url == "/api/v2/application/apply-demo-claims-app" and request.method == "GET":
            nonlocal t
            if t == 1:
                resp = requests.Response()
                resp.status_code = 404
                resp._content = json.dumps({}).encode("utf-8")
            elif t == 2:
                resp = requests.Response()
                resp.status_code = 200
                resp._content = json.dumps({
                    'id': 1,
                    "name": "app",
                    'status': 'Assembling',
                    "signature": {
                        "signatureName": "predict",
                        "inputs": [],
                        "outputs": []
                    },
                    "executionGraph": {
                        "stages": [{
                                "signature": {
                                    "signatureName": "predict",
                                    "inputs": [],
                                    "outputs": []
                                },
                                "modelVariants": [{
                                    "modelVersionId": 1,
                                    "servableName": "test-name",
                                    "deploymentConfigurationName": None,
                                    "weight": 100
                                }]
                            }]
                    },
                    "kafkaStreaming": []
                }).encode("utf-8")
            else:
                resp = requests.Response()
                resp.status_code = 200
                resp._content = json.dumps({
                    'id': 1,
                    "name": "app",
                    'status': 'Ready',
                    "signature": {
                        "signatureName": "predict",
                        "inputs": [],
                        "outputs": []
                    },
                    "executionGraph": {
                        "stages": [{
                                "signature": {
                                    "signatureName": "predict",
                                    "inputs": [],
                                    "outputs": []
                                },
                                "modelVariants": [{
                                    "modelVersionId": 1,
                                    "servableName": "test-name",
                                    "deploymentConfigurationName": None,
                                    "weight": 100
                                }]
                            }]
                    },
                    "kafkaStreaming": []
                }).encode("utf-8")
            t = t + 1
        elif request.path_url == "/api/v2/application" and request.method == "POST":
            resp = requests.Response()
            resp.status_code = 200
            resp._content = json.dumps({
                    'id': 1,
                    "name": "app",
                    'status': 'Ready',
                    "signature": {
                        "signatureName": "predict",
                        "inputs": [],
                        "outputs": []
                    },
                    "executionGraph": {
                        "stages": [{
                                "signature": {
                                    "signatureName": "predict",
                                    "inputs": [],
                                    "outputs": []
                                },
                                "modelVariants": [{
                                    "modelVersionId": 1,
                                    "servableName": "test-name",
                                    "deploymentConfigurationName": None,
                                    "weight": 100
                                }]
                            }]
                    },
                    "kafkaStreaming": []
                }).encode("utf-8")
        return resp

    with requests_mock.Mocker() as req_mock:
        req_mock.add_matcher(_upload_matcher)
        runner = CliRunner()
        result = runner.invoke(hs_cli, ["-v", "--config-file", cluster_config, "apply", "-f", "./examples/full-apply-example/4-claims-app.yml"], catch_exceptions=False)
        print(result.output)
        assert result.exit_code == 0

def test_application_pipeline_apply(cluster_config):
    t = 1
    def _upload_matcher(request):
        resp = None
        if request.path_url == '/api/v2/model/version/claims-preprocessing/1':
            resp = requests.Response()
            resp.status_code = 200
            resp._content = json.dumps(
                {
                    "id": 1,
                    "model": {"name": "claims-preprocessing", "id": 1},
                    "modelVersion": 1,
                    "status": "Released",
                    "modelSignature": {
                        "signatureName": "predict",
                        "inputs": [],
                        "outputs": []
                    },
                    "monitoringConfiguration": {
                        "batchSize": 100
                    },
                    "runtime": {
                        "name": "python",
                        "tag": "latest"
                    },
                    "metadata": {}
                }
            ).encode("utf-8")
        elif request.path_url == '/api/v2/model/version/claims-model/1':
            resp = requests.Response()
            resp.status_code = 200
            resp._content = json.dumps(
                {
                    "id": 2,
                    "model": {"name": "claims-model", "id": 2},
                    "modelVersion": 1,
                    "status": "Released",
                    "modelSignature": {
                        "signatureName": "predict",
                        "inputs": [],
                        "outputs": []
                    },
                    "monitoringConfiguration": {
                        "batchSize": 100
                    },
                    "runtime": {
                        "name": "python",
                        "tag": "latest"
                    },
                    "metadata": {}
                }
            ).encode("utf-8")
        elif request.path_url == '/api/v2/model/version/claims-model/2':
            resp = requests.Response()
            resp.status_code = 200
            resp._content = json.dumps(
                {
                    "id": 3,
                    "model": {"name": "claims-model", "id": 2},
                    "modelVersion": 1,
                    "status": "Released",
                    "modelSignature": {
                        "signatureName": "predict",
                        "inputs": [],
                        "outputs": []
                    },
                    "monitoringConfiguration": {
                        "batchSize": 100
                    },
                    "runtime": {
                        "name": "python",
                        "tag": "latest"
                    },
                    "metadata": {}
                }
            ).encode("utf-8")
        elif request.path_url == '/api/v2/application/claims-pipeline-app' and request.method == "GET":
            nonlocal t
            if t == 1:
                resp = requests.Response()
                resp.status_code = 404
                resp._content = json.dumps({}).encode("utf-8")
            else:
                resp = requests.Response()
                resp.status_code = 200
                resp._content = json.dumps({
                    'id': 1,
                    'status': 'Ready'
                }).encode('utf-8')
            t = t + 1
        elif request.path_url == '/api/v2/application' and request.method == "POST":
            resp = requests.Response()
            resp.status_code = 200
            resp._content = json.dumps({
                    'id': 1,
                    "name": "app",
                    'status': 'Assembling',
                    "signature": {
                        "signatureName": "predict",
                        "inputs": [],
                        "outputs": []
                    },
                    "executionGraph": {
                        "stages": [{
                                "signature": {
                                    "signatureName": "predict",
                                    "inputs": [],
                                    "outputs": []
                                },
                                "modelVariants": [{
                                    "modelVersionId": 1,
                                    "servableName": "test-name",
                                    "deploymentConfigurationName": None,
                                    "weight": 100
                                }]
                            }]
                    },
                    "kafkaStreaming": []
                }).encode("utf-8")
        return resp

    with requests_mock.Mocker() as req_mock:
        req_mock.add_matcher(_upload_matcher)
        runner = CliRunner()
        result = runner.invoke(hs_cli, ["-v", "--config-file", cluster_config, "apply", "-f", "./examples/full-apply-example/5-claims-pipeline-app.yml"], catch_exceptions=False)
        print(result.output)
        assert result.exit_code == 0
