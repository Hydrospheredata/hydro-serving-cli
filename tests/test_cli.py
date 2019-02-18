import json
import os
import unittest

import requests
import requests_mock

from hydroserving.core.application.service import ApplicationService
from hydroserving.core.apply import ApplyService
from hydroserving.core.host_selector.host_selector import HostSelectorService
from hydroserving.core.model.parser import parse_model
from hydroserving.core.model.service import ModelService
from hydroserving.core.model.upload import upload_model
from hydroserving.core.monitoring.service import MonitoringService
from hydroserving.core.profiler import ProfilerService
from hydroserving.http.remote_connection import RemoteConnection
from hydroserving.util.yamlutil import yaml_file

MODEL_FOLDER = "./examples/local_dev"


class CLITests(unittest.TestCase):
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
                        "model_name": "example_script",
                        "model_type": "python:3.6"
                    }
                ).encode("utf-8")
                return resp
            return None

        with requests_mock.Mocker() as req_mock:
            req_mock.add_matcher(_upload_matcher)
            connection = RemoteConnection("http://localhost")
            profiler_service = ProfilerService(connection)
            monitoring_service = MonitoringService(connection)
            model_api = ModelService(connection, profiler_service, monitoring_service)
            yaml_path = os.path.join(MODEL_FOLDER, "serving.yaml")
            with open(yaml_path, 'r') as f:
                yaml_dict = yaml_file(f)
                meta = parse_model(yaml_dict)
                result = upload_model(
                    model_service=model_api,
                    profiler_service=profiler_service,
                    monitoring_service=monitoring_service,
                    model=meta,
                    model_path=yaml_path,
                    is_async=True,
                    no_training_data=True,
                    ignore_monitoring=True)
                assert "example_script" in result["model_name"]
                assert "python:3.6" in result["model_type"]

    def test_model_apply(self):
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
                        "model_name": "example_script",
                        "model_type": "python:3.6"
                    }
                ).encode("utf-8")
                return resp
            return None

        with requests_mock.Mocker() as req_mock:
            req_mock.add_matcher(_upload_matcher)
            connection = RemoteConnection("http://localhost")
            profiler_service = ProfilerService(connection)
            monitoring_service = MonitoringService(connection)
            model_api = ModelService(connection, profiler_service, monitoring_service)
            apply_api = ApplyService(model_api, None, None)
            yaml_path = os.path.join(MODEL_FOLDER, "serving.yaml")
            result = apply_api.apply([yaml_path], ignore_monitoring=True, no_training_data=True)
            assert "example_script" in result["model_name"]
            assert "python:3.6" in result["model_type"]

    def test_application_singular_apply(self):
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
                        "model_name": "example_script",
                        "model_type": "python:3.6"
                    }
                ).encode("utf-8")
                return resp
            return None

        with requests_mock.Mocker() as req_mock:
            req_mock.add_matcher(_upload_matcher)
            connection = RemoteConnection("http://localhost")
            profiler_service = ProfilerService(connection)
            monitoring_service = MonitoringService(connection)
            model_api = ModelService(connection, profiler_service, monitoring_service)
            application_api = ApplicationService(connection, model_api)
            apply_service = ApplyService(model_api, None, application_api)
            result = apply_service.apply(["./examples/full-apply-example/5-claims-app.yml"])
            assert "example_script" in result["model_name"]
            assert "python:3.6" in result["model_type"]

    def test_application_pipeline_apply(self):
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
                        "model_name": "example_script",
                        "model_type": "python:3.6"
                    }
                ).encode("utf-8")
                return resp
            return None

        with requests_mock.Mocker() as req_mock:
            req_mock.add_matcher(_upload_matcher)
            connection = RemoteConnection("http://localhost")
            profiler_service = ProfilerService(connection)
            monitoring_service = MonitoringService(connection)
            model_api = ModelService(connection, profiler_service, monitoring_service)
            application_api = ApplicationService(connection, model_api)
            apply_service = ApplyService(model_api, None, application_api)
            result = apply_service.apply(["./examples/full-apply-example/6-claims-pipeline-app.yml"])
            assert "example_script" in result["model_name"]
            assert "python:3.6" in result["model_type"]

    def test_host_selector_apply(self):
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
                        "model_name": "example_script",
                        "model_type": "python:3.6"
                    }
                ).encode("utf-8")
                return resp
            return None

        with requests_mock.Mocker() as req_mock:
            req_mock.add_matcher(_upload_matcher)
            connection = RemoteConnection("http://localhost")
            profiler_service = ProfilerService(connection)
            monitoring_service = MonitoringService(connection)
            model_api = ModelService(connection, profiler_service, monitoring_service)
            application_api = ApplicationService(connection, model_api)
            selector_api = HostSelectorService(connection)
            apply_service = ApplyService(model_api, selector_api, application_api)
            result = apply_service.apply(["./examples/full-apply-example/1-intel-xeon-env.yml"])
            assert "example_script" in result["model_name"]
            assert "python:3.6" in result["model_type"]
