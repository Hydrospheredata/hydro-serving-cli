import json
import os
import unittest

import requests
import requests_mock

from hydroserving.constants.package import TARGET_FOLDER
from hydroserving.helpers.upload import upload_model
from hydroserving.httpclient import HydroservingClient
from hydroserving.parsers.model import ModelParser
from tests.utils import with_target_cwd

MODEL_FOLDER = "./examples/new_metadata"


def build_example(hs_api):
    yaml_path = os.path.join(os.getcwd(), "serving.yml")
    meta = ModelParser().parse_yaml(yaml_path)
    return upload_model(hs_api.models, meta, TARGET_FOLDER)


class CLITests(unittest.TestCase):
    def test_model_upload(self):
        def _test_model_upload():
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
                hs_api = HydroservingClient("http://localhost")
                result = build_example(hs_api)
                assert "example_script" in result["model_name"]
                assert "python:3.6" in result["model_type"]

        with_target_cwd(MODEL_FOLDER, _test_model_upload)
