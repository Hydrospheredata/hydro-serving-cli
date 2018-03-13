import os
import unittest


from hydroserving.helpers.package import with_cwd
from hydroserving.helpers.upload import upload_model
from hydroserving.httpclient import HydroservingClient
from hydroserving.httpclient.remote_connection import RemoteConnection
from hydroserving.models import FolderMetadata


class MockConnection(RemoteConnection):
    MOCKS = {
        "/api/v1/model": [],
        "/api/v1/runtime": [],
        "/api/v1/model/version": []
    }

    def get_mock(self, url):
        print("Mock GET {} call".format(url))
        return MockConnection.MOCKS[url]

    def post_mock(self, url, data):
        print("Mock POST {} call".format(url))
        return data

    def __init__(self):
        super().__init__("http://127.0.0.1")

    def send_request(self, request):
        if request.data is None:
            return self.get_mock(request.selector)
        else:
            return self.post_mock(request.selector, request.data)

    def send_multipart(self, url, multipart_monitor):
        return multipart_monitor.encoder.fields


def build_example(hs_api):
    meta = FolderMetadata.from_directory(os.getcwd())
    return upload_model(hs_api.models, None, meta.model)


class HttpClientCase(unittest.TestCase):
    def test_model_list(self):
        connection = MockConnection()
        model_api = HydroservingClient(connection)
        model_api.models.list()

    def test_model_list_versions(self):
        connection = MockConnection()
        model_api = HydroservingClient(connection)
        model_api.models.list_versions()

    def test_model_find_version(self):
        connection = MockConnection()
        model_api = HydroservingClient(connection)
        model_api.models.find_version("test", 1)

    def test_model_build(self):
        connection = MockConnection()
        model_api = HydroservingClient(connection)
        model_api.models.build(1)

    def test_model_upload(self):
        connection = MockConnection()
        hs_api = HydroservingClient(connection)
        result = with_cwd("examples/local_dev", build_example, hs_api)
        assert "example_script" in result["model_name"]
        assert "python:3.6" in result["model_type"]
        assert result["payload"] is not None


if __name__ == "__main__":
    unittest.main()
