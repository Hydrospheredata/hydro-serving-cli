import json
import os
import unittest

import requests
import requests_mock

from hydroserving.config.settings import TARGET_FOLDER
from hydroserving.core.model.parser import ModelParser
from hydroserving.core.model.service import ModelService
from hydroserving.core.model.upload import upload_model
from hydroserving.core.profiler import ProfilerService
from hydroserving.http.remote_connection import RemoteConnection
from tests.utils import with_target_cwd

MODEL_FOLDER = "./examples/new_metadata"


class CLITests(unittest.TestCase):
    def test_model_upload(self):
        def _upload_matcher(request):
            if request.path_url == "/api/v1/model/upload":
                fields = request.text.encoder.fields
                assert 'model_contract' in fields
                assert 'payload' in fields
                assert fields['model_type'] == "python:3.6"
                assert fields["model_name"] == "claims-model"
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
            model_api = ModelService(connection)
            profiler_api = ProfilerService(connection)
            yaml_path = os.path.join(MODEL_FOLDER, "serving.yml")
            meta = ModelParser().yaml_file(yaml_path)
            result = upload_model(model_api, profiler_api, meta, TARGET_FOLDER, is_async=True)
            assert "example_script" in result["model_name"]
            assert "python:3.6" in result["model_type"]

