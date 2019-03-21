import json
import os
import unittest
from click.testing import CliRunner
import requests
import requests_mock

from hydroserving.cli.commands.hs import hs_cli
from hydroserving.core.application.service import ApplicationService
from hydroserving.core.apply import ApplyService
from hydroserving.core.host_selector.host_selector import HostSelectorService
from hydroserving.core.model.parser import parse_model
from hydroserving.core.model.service import ModelService
from hydroserving.core.model.upload import upload_model
from hydroserving.core.monitoring.service import MonitoringService
from hydroserving.http.remote_connection import RemoteConnection
from hydroserving.util.yamlutil import yaml_file

MODEL_FOLDER = "./examples/local_dev"


class CLITests(unittest.TestCase):
    def test_hs(self):
        runner = CliRunner()
        result = runner.invoke(hs_cli)
        print(result)
        assert result.exit_code == 0

    def test_model_upload(self):
        def _upload_matcher(request):
            if request.path_url == "/api/v2/model/upload":
                fields = request.text.fields
                assert 'metadata' in fields
                assert 'payload' in fields
                metadata = json.loads(fields['metadata'])
                print(metadata)
                assert metadata["name"] == "example_script"
                assert metadata["installCommand"] == "pip install -r requirements.txt"
                assert metadata["hostSelectorName"] is None
                resp = requests.Response()
                resp.status_code = 200
                resp._content = json.dumps(
                    {
                        "model": {"name": "example_script"},
                        "modelVersion": 1
                    }
                ).encode("utf-8")
                return resp
            elif request.path_url == '/api/v2/model/version/example_script/1':
                resp = requests.Response()
                resp.status_code = 200
                resp._content = json.dumps(
                    {
                        "model": {"name": "example_script"},
                        "modelVersion": 1,
                        "status": "KEK"
                    }
                ).encode("utf-8")
                return resp
            return None

        with requests_mock.Mocker() as req_mock:
            req_mock.add_matcher(_upload_matcher)
            connection = RemoteConnection("http://localhost")
            monitoring_service = MonitoringService(connection)
            model_api = ModelService(connection, monitoring_service)
            yaml_path = os.path.join(MODEL_FOLDER, "serving.yaml")
            with open(yaml_path, 'r') as f:
                yaml_dict = yaml_file(f)
                meta = parse_model(yaml_dict)
                result = upload_model(
                    model_service=model_api,
                    monitoring_service=monitoring_service,
                    model=meta,
                    model_path=yaml_path,
                    is_async=True,
                    ignore_training_data=True,
                    ignore_monitoring=True)
                assert "example_script" == result["model"]["name"]
                assert 1 == result["modelVersion"]

    def test_model_apply(self):
        def _upload_matcher(request):
            resp = None
            if request.path_url == "/api/v2/model/upload":
                fields = request.text.fields
                assert 'metadata' in fields
                assert 'payload' in fields
                metadata = json.loads(fields['metadata'])
                m = metadata["metadata"]
                print(metadata)
                assert metadata["name"] == "apply-demo-claims-model"
                assert metadata["hostSelectorName"] is None
                assert m["author"] == "cool-data-stan"
                resp = requests.Response()
                resp.status_code = 200
                resp._content = json.dumps(
                    {
                        "id": 1,
                        "model": {"name": "apply-demo-claims-model"},
                        "modelVersion": 1,
                        "status": "Pending"
                    }
                ).encode("utf-8")
            elif request.path_url == '/api/v2/model/version/apply-demo-claims-model/1':
                resp = requests.Response()
                resp.status_code = 200
                resp._content = json.dumps(
                    {
                        "id": 1,
                        "model": {"name": "apply-demo-claims-model"},
                        "modelVersion": 1,
                        "status": "Released"
                    }
                ).encode("utf-8")
            elif request.path_url == "/monitoring/metricspec" and request.method == "POST":
                d = json.loads(request.text)
                print(d)
                assert d["modelVersionId"] == 1
                resp = requests.Response()
                resp.status_code = 200
                resp._content = request.text.encode("utf-8")
            return resp

        with requests_mock.Mocker() as req_mock:
            req_mock.add_matcher(_upload_matcher)
            connection = RemoteConnection("http://localhost")
            monitoring_service = MonitoringService(connection)
            model_api = ModelService(connection, monitoring_service)
            apply_api = ApplyService(model_api, None, None)
            yaml_path = os.path.join("./examples/full-apply-example/3-claims-model.yml")
            result = apply_api.apply([yaml_path], ignore_monitoring=False, no_training_data=False)
            print(result)
            assert "Released" == result["./examples/full-apply-example"][0]["status"]

    def test_application_singular_apply(self):
        def _upload_matcher(request):
            resp = None
            if request.path_url == "/api/v2/model/version/apply-demo-claims-model/2":
                resp = requests.Response()
                resp.status_code = 200
                resp._content = json.dumps(
                    {
                        "id": 1,
                        "model": {"name": "apply-demo-claims-model"},
                        "modelVersion": 2,
                        "status": "Ready"
                    }
                ).encode("utf-8")
            elif request.path_url == "/api/v2/application/apply-demo-claims-app" and request.method == "GET":
                resp = requests.Response()
                resp.status_code = 404
                resp._content = json.dumps([]).encode("utf-8")
            elif request.path_url == "/api/v2/application" and request.method == "POST":
                req = json.loads(request.text)
                variant1 = req["executionGraph"]["stages"][0]["modelVariants"][0]
                self.assertEqual(variant1["modelVersionId"], 1)
                self.assertEqual(variant1["weight"], 100)
                self.assertEqual(req["name"], "apply-demo-claims-app")

                resp = requests.Response()
                resp.status_code = 200
                resp._content = json.dumps({"id": 1}).encode("utf-8")
            return resp

        with requests_mock.Mocker() as req_mock:
            req_mock.add_matcher(_upload_matcher)
            connection = RemoteConnection("http://localhost")
            monitoring_service = MonitoringService(connection)
            model_api = ModelService(connection, monitoring_service)
            application_api = ApplicationService(connection, model_api)
            apply_service = ApplyService(model_api, None, application_api)
            result = apply_service.apply(["./examples/full-apply-example/5-claims-app.yml"])
            assert 1 == result['./examples/full-apply-example'][0]['id']

    def test_application_pipeline_apply(self):
        def _upload_matcher(request):
            resp = None
            if request.path_url == '/api/v2/model/version/claims-preprocessing/1':
                resp = requests.Response()
                resp.status_code = 200
                resp._content = json.dumps(
                    {
                        "id": 1,
                        "model": {"name": "claims-preprocessing"},
                        "modelVersion": 1,
                        "status": "Ready"
                    }
                ).encode("utf-8")
            elif request.path_url == '/api/v2/model/version/claims-model/1':
                resp = requests.Response()
                resp.status_code = 200
                resp._content = json.dumps(
                    {
                        "id": 2,
                        "model": {"name": "claims-model"},
                        "modelVersion": 1,
                        "status": "Ready"
                    }
                ).encode("utf-8")
            elif request.path_url == '/api/v2/model/version/claims-model/2':
                resp = requests.Response()
                resp.status_code = 200
                resp._content = json.dumps(
                    {
                        "id": 3,
                        "model": {"name": "claims-model"},
                        "modelVersion": 2,
                        "status": "Ready"
                    }
                ).encode("utf-8")
            elif request.path_url == '/api/v2/application/claims-pipeline-app' and request.method == "GET":
                resp = requests.Response()
                resp.status_code = 404
                resp._content = json.dumps({}).encode("utf-8")
            elif request.path_url == '/api/v2/application' and request.method == "POST":
                req = json.loads(request.text)
                print(req)
                variant1 = req["executionGraph"]["stages"][0]["modelVariants"][0]
                assert variant1["modelVersionId"] == 1
                assert variant1["weight"] == 100

                variant2 = req["executionGraph"]["stages"][1]["modelVariants"][0]
                assert variant2["modelVersionId"] == 2
                assert variant2["weight"] == 80

                variant3 = req["executionGraph"]["stages"][1]["modelVariants"][1]
                assert variant3["modelVersionId"] == 3
                assert variant3["weight"] == 20
                assert req["name"] == "claims-pipeline-app"

                resp = requests.Response()
                resp.status_code = 200
                resp._content = json.dumps({
                    "id": 1
                }).encode("utf-8")
            return resp

        with requests_mock.Mocker() as req_mock:
            req_mock.add_matcher(_upload_matcher)
            connection = RemoteConnection("http://localhost")
            monitoring_service = MonitoringService(connection)
            model_api = ModelService(connection, monitoring_service)
            application_api = ApplicationService(connection, model_api)
            apply_service = ApplyService(model_api, None, application_api)
            result = apply_service.apply(["./examples/full-apply-example/6-claims-pipeline-app.yml"])
            assert 1 == result['./examples/full-apply-example'][0]['id']

    def test_application_update_apply(self):
        def _upload_matcher(request):
            resp = None
            if request.path_url == "/api/v2/model/version/apply-demo-claims-model/2":
                resp = requests.Response()
                resp.status_code = 200
                resp._content = json.dumps(
                    {
                        "id": 1,
                        "model": {"name": "apply-demo-claims-model"},
                        "modelVersion": 2,
                        "status": "Ready"
                    }
                ).encode("utf-8")
            elif request.path_url == "/api/v2/application/apply-demo-claims-app" and request.method == "GET":
                resp = requests.Response()
                resp.status_code = 200
                resp._content = json.dumps({
                    "id": 1
                }).encode("utf-8")
            elif request.path_url == "/api/v2/application" and request.method == "PUT":
                req = json.loads(request.text)
                variant = req["executionGraph"]["stages"][0]["modelVariants"][0]
                assert variant["modelVersionId"] == 1
                assert variant["weight"] == 100
                assert req["name"] == "apply-demo-claims-app"
                assert req["id"] == 1
                resp = requests.Response()
                resp.status_code = 200
                resp._content = json.dumps({"id": 1}).encode("utf-8")
            return resp

        with requests_mock.Mocker() as req_mock:
            req_mock.add_matcher(_upload_matcher)
            connection = RemoteConnection("http://localhost")
            monitoring_service = MonitoringService(connection)
            model_api = ModelService(connection, monitoring_service)
            application_api = ApplicationService(connection, model_api)
            apply_service = ApplyService(model_api, None, application_api)
            result = apply_service.apply(["./examples/full-apply-example/5-claims-app.yml"])
            assert 1 == result['./examples/full-apply-example'][0]['id']

    def test_host_selector_new_apply(self):
        def _upload_matcher(request):
            resp = None
            if request.path_url == "/api/v2/hostSelector/xeon-cpu" and request.method == "GET":
                resp = requests.Response()
                resp.status_code = 404
                resp._content = json.dumps({}).encode("utf-8")
            elif request.path_url == "/api/v2/hostSelector" and request.method == "POST":
                resp = requests.Response()
                resp.status_code = 200
                resp._content = json.dumps({"id": 1}).encode("utf-8")
            return resp

        with requests_mock.Mocker() as req_mock:
            req_mock.add_matcher(_upload_matcher)
            connection = RemoteConnection("http://localhost")
            monitoring_service = MonitoringService(connection)
            model_api = ModelService(connection, monitoring_service)
            application_api = ApplicationService(connection, model_api)
            selector_api = HostSelectorService(connection)
            apply_service = ApplyService(model_api, selector_api, application_api)
            result = apply_service.apply(["./examples/full-apply-example/1-intel-xeon-env.yml"])
            assert 1 == result["./examples/full-apply-example"][0]["id"]

    def test_host_selector_existing_apply(self):
        def _upload_matcher(request):
            resp = None
            if request.path_url == "/api/v2/hostSelector/xeon-cpu" and request.method == "GET":
                resp = requests.Response()
                resp.status_code = 200
                resp._content = json.dumps({"id": 1}).encode("utf-8")
            return resp

        with requests_mock.Mocker() as req_mock:
            req_mock.add_matcher(_upload_matcher)
            connection = RemoteConnection("http://localhost")
            monitoring_service = MonitoringService(connection)
            model_api = ModelService(connection, monitoring_service)
            application_api = ApplicationService(connection, model_api)
            selector_api = HostSelectorService(connection)
            apply_service = ApplyService(model_api, selector_api, application_api)
            result = apply_service.apply(["./examples/full-apply-example/1-intel-xeon-env.yml"])
            res = result["./examples/full-apply-example"]
            assert len(res) == 1
            assert res[0] is None
