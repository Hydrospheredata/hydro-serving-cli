from io import BytesIO
import json
import os
import tempfile
import pytest
import requests
import requests_mock
import logging
from click.testing import CliRunner

from hs.cli.commands import hs_cli
from hs.entities.model_version import ModelVersion
from hs.entities.cluster_config import ClusterConfig, ClusterDef, ClusterServerDef


logging.root.setLevel(logging.DEBUG)
MODEL_FOLDER = "./examples/local_dev"

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
            resp = requests.Response()
            resp.status_code = 200
            resp.headers["Content-Type"] = "text/event-stream"
            resp.raw = BytesIO("data: Hello there".encode("utf-8"))
        return resp

    with requests_mock.Mocker() as req_mock:
        req_mock.add_matcher(_upload_matcher)

        runner = CliRunner()
        result = runner.invoke(hs_cli, ["-v", "--config-file", cluster_config, "apply", "-f", "./examples/full-apply-example/3-claims-model.yml"], catch_exceptions=False)
        mv: ModelVersion = ModelVersion.parse_file("./examples/full-apply-example/3-claims-model.yml")
        print(result.output)
        # if result.exception:
        #     raise result.exception
        assert result.exit_code == 0

# def test_application_singular_apply():
#     t = 1

#     def _upload_matcher(request):
#         resp = None
#         if request.path_url == "/api/v2/model/version/apply-demo-claims-model/2":
#             resp = requests.Response()
#             resp.status_code = 200
#             resp._content = json.dumps(
#                 {
#                     "id": 1,
#                     "model": {"name": "apply-demo-claims-model"},
#                     "modelVersion": 2,
#                     "status": "Ready"
#                 }
#             ).encode("utf-8")
#         elif request.path_url == "/api/v2/application/apply-demo-claims-app" and request.method == "GET":
#             nonlocal t
#             if t == 1:
#                 resp = requests.Response()
#                 resp.status_code = 404
#                 resp._content = json.dumps({}).encode("utf-8")
#             elif t == 2:
#                 resp = requests.Response()
#                 resp.status_code = 200
#                 resp._content = json.dumps({
#                     'id': 1,
#                     'status': 'Assembling'
#                 }).encode("utf-8")
#             else:
#                 resp = requests.Response()
#                 resp.status_code = 200
#                 resp._content = json.dumps({
#                     'id': 1,
#                     'status': 'Ready'
#                 }).encode("utf-8")
#             t = t + 1
#         elif request.path_url == "/api/v2/application" and request.method == "POST":
#             req = json.loads(request.text)
#             variant1 = req["executionGraph"]["stages"][0]["modelVariants"][0]
#             self.assertEqual(variant1["modelVersionId"], 1)
#             self.assertEqual(variant1["weight"], 100)
#             self.assertEqual(req["name"], "apply-demo-claims-app")

#             resp = requests.Response()
#             resp.status_code = 200
#             resp._content = json.dumps({"id": 1}).encode("utf-8")
#         return resp

#     with requests_mock.Mocker() as req_mock:
#         req_mock.add_matcher(_upload_matcher)
#         connection = RemoteConnection("http://localhost")
#         monitoring_service = MonitoringService(connection)
#         model_api = ModelService(connection, monitoring_service)
#         application_api = ApplicationService(connection, model_api)
#         apply_service = ApplyService(model_api, application_api, None)
#         result = apply_service.apply(["./examples/full-apply-example/4-claims-app.yml"])

# def test_application_pipeline_apply():
#     t = 1

#     def _upload_matcher(request):
#         resp = None
#         if request.path_url == '/api/v2/model/version/claims-preprocessing/1':
#             resp = requests.Response()
#             resp.status_code = 200
#             resp._content = json.dumps(
#                 {
#                     "id": 1,
#                     "model": {"name": "claims-preprocessing"},
#                     "modelVersion": 1,
#                     "status": "Ready"
#                 }
#             ).encode("utf-8")
#         elif request.path_url == '/api/v2/model/version/claims-model/1':
#             resp = requests.Response()
#             resp.status_code = 200
#             resp._content = json.dumps(
#                 {
#                     "id": 2,
#                     "model": {"name": "claims-model"},
#                     "modelVersion": 1,
#                     "status": "Ready"
#                 }
#             ).encode("utf-8")
#         elif request.path_url == '/api/v2/model/version/claims-model/2':
#             resp = requests.Response()
#             resp.status_code = 200
#             resp._content = json.dumps(
#                 {
#                     "id": 3,
#                     "model": {"name": "claims-model"},
#                     "modelVersion": 2,
#                     "status": "Ready"
#                 }
#             ).encode("utf-8")
#         elif request.path_url == '/api/v2/application/claims-pipeline-app' and request.method == "GET":
#             nonlocal t
#             if t == 1:
#                 resp = requests.Response()
#                 resp.status_code = 404
#                 resp._content = json.dumps({}).encode("utf-8")
#             else:
#                 resp = requests.Response()
#                 resp.status_code = 200
#                 resp._content = json.dumps({
#                     'id': 1,
#                     'status': 'Ready'
#                 }).encode('utf-8')
#             t = t + 1
#         elif request.path_url == '/api/v2/application' and request.method == "POST":
#             req = json.loads(request.text)
#             print(req)
#             variant1 = req["executionGraph"]["stages"][0]["modelVariants"][0]
#             assert variant1["modelVersionId"] == 1
#             assert variant1["weight"] == 100

#             variant2 = req["executionGraph"]["stages"][1]["modelVariants"][0]
#             assert variant2["modelVersionId"] == 2
#             assert variant2["weight"] == 80

#             variant3 = req["executionGraph"]["stages"][1]["modelVariants"][1]
#             assert variant3["modelVersionId"] == 3
#             assert variant3["weight"] == 20
#             assert req["name"] == "claims-pipeline-app"

#             resp = requests.Response()
#             resp.status_code = 200
#             resp._content = json.dumps({
#                 "id": 1
#             }).encode("utf-8")
#         return resp

#     with requests_mock.Mocker() as req_mock:
#         req_mock.add_matcher(_upload_matcher)
#         connection = RemoteConnection("http://localhost")
#         monitoring_service = MonitoringService(connection)
#         model_api = ModelService(connection, monitoring_service)
#         application_api = ApplicationService(connection, model_api)
#         apply_service = ApplyService(model_api, application_api, None)
#         result = apply_service.apply(["./examples/full-apply-example/5-claims-pipeline-app.yml"])

# def test_application_update_apply():
#     def _upload_matcher(request):
#         resp = None
#         if request.path_url == "/api/v2/model/version/apply-demo-claims-model/2":
#             resp = requests.Response()
#             resp.status_code = 200
#             resp._content = json.dumps(
#                 {
#                     "id": 1,
#                     "model": {"name": "apply-demo-claims-model"},
#                     "modelVersion": 2,
#                     "status": "Ready"
#                 }
#             ).encode("utf-8")
#         elif request.path_url == "/api/v2/application/apply-demo-claims-app" and request.method == "GET":
#             resp = requests.Response()
#             resp.status_code = 200
#             resp._content = json.dumps({
#                 "id": 1,
#                 "status": "Ready"
#             }).encode("utf-8")
#         elif request.path_url == "/api/v2/application" and request.method == "PUT":
#             req = json.loads(request.text)
#             variant = req["executionGraph"]["stages"][0]["modelVariants"][0]
#             assert variant["modelVersionId"] == 1
#             assert variant["weight"] == 100
#             assert req["name"] == "apply-demo-claims-app"
#             assert req["id"] == 1
#             resp = requests.Response()
#             resp.status_code = 200
#             resp._content = json.dumps({"id": 1}).encode("utf-8")
#         return resp

#     with requests_mock.Mocker() as req_mock:
#         req_mock.add_matcher(_upload_matcher)
#         connection = RemoteConnection("http://localhost")
#         monitoring_service = MonitoringService(connection)
#         model_api = ModelService(connection, monitoring_service)
#         application_api = ApplicationService(connection, model_api)
#         apply_service = ApplyService(model_api, application_api, None)
#         result = apply_service.apply(["./examples/full-apply-example/4-claims-app.yml"])
