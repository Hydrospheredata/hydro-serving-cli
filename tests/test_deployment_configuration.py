import json
import os
import unittest

import requests
import requests_mock

from hydroserving.core.apply import ApplyService
from hydroserving.core.deployment_config.service import DeploymentConfigurationService
from hydroserving.http.remote_connection import RemoteConnection

MODEL_FOLDER = "./examples/local_dev"


class DeploymentConfigurationTests(unittest.TestCase):

    def test_deployment_configuration_apply(self):
        def _upload_matcher(request):
            if request.path_url == "/api/v2/deployment_configuration":
                payload = request.json()
                resp = requests.Response()
                resp.status_code = 200
                resp._content = json.dumps(payload).encode("utf-8")
                return resp

        with requests_mock.Mocker() as req_mock:
            req_mock.add_matcher(_upload_matcher)
            connection = RemoteConnection("http://localhost")
            service = DeploymentConfigurationService(connection)
            apply_api = ApplyService(None, None, deployment_configuration_service=service)

            current_dir = os.path.dirname(os.path.abspath(__file__))
            yaml_path = os.path.join(current_dir, 'resources/deployment_configuration.yaml')
            result = apply_api.apply([yaml_path])
            print(result)
