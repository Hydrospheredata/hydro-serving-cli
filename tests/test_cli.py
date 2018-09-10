import os
import json
import yaml

import requests
import requests_mock
from click.testing import CliRunner

from hydroserving.models.definitions.model import Model
from hydroserving.cli import hs_cli
from hydroserving.helpers.package import with_cwd
from hydroserving.helpers.upload import upload_model
from hydroserving.httpclient import HydroservingClient
from tests.utils import with_target_cwd

MODEL_FOLDER = "./examples/new_metadata"


def build_example(hs_api):
    yaml_path = os.path.join(os.getcwd(), "serving.yml")
    with open(yaml_path, "r") as f:
        yaml_dict = yaml.safe_load(f)
    meta = Model.from_dict(yaml_dict)
    return upload_model(hs_api.models, meta)


def test_incorrect_status():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(hs_cli, ["status"])
        print(result)
        assert result.exit_code == 0


def test_correct_status():
    def _test_correct_status():
        runner = CliRunner()
        result = runner.invoke(hs_cli, ["status"])
        assert result.exit_code == 0
        assert "claims-model" in result.output

    with_cwd(MODEL_FOLDER, _test_correct_status)


def test_model_upload():
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
