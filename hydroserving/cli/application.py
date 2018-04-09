from hydroserving.cli.hs import hs_cli
from hydroserving.cli.utils import ensure_app_data
from hydroserving.constants.help import *
from hydroserving.helpers.deployment import *
from hydroserving.httpclient.api import ApplicationAPI
from hydroserving.httpclient.remote_connection import RemoteConnection
from hydroserving.models.application import Application


@hs_cli.group(help=APPLICATION_HELP)
@click.pass_obj
def app(obj):
    obj.app_data = Application.from_directory(os.getcwd())


@app.command()
@click.option('--host',
              default="localhost",
              show_default=True,
              help=UPLOAD_HOST_HELP,
              required=False)
@click.option('--port',
              default=9090,
              show_default=True,
              help=UPLOAD_PORT_HELP,
              required=False)
@click.pass_obj
def deploy(obj, host, port):
    app = ensure_app_data(obj)
    remote = RemoteConnection("http://{}:{}".format(host, port))
    app_api = ApplicationAPI(remote)
    app_api.list()
    click.echo(app.__dict__)


@app.command()
@click.option('--host',
              default="localhost",
              show_default=True,
              help=UPLOAD_HOST_HELP,
              required=False)
@click.option('--port',
              default=9090,
              show_default=True,
              help=UPLOAD_PORT_HELP,
              required=False)
@click.pass_obj
def list(obj, host, port):
    remote = StubConnection()
    app_api = ApplicationAPI(remote)
    apps = app_api.list()
    click.echo(apps)
    raise NotImplementedError()


class StubConnection(RemoteConnection):
    def __init__(self):
        super().__init__("")

    def get(self, url):
        return [
            {
                "name": "weighted_application",
                "kafkaStreaming": [
                    {
                        "sourceTopic": "test_weight",
                        "destinationTopic": "success_weight",
                        "consumerId": "test_weight",
                        "errorTopic": "failure_weight"
                    }
                ],
                "id": 2,
                "executionGraph": {
                    "stages": [
                        {
                            "services": [
                                {
                                    "serviceDescription": {
                                        "runtimeId": 2,
                                        "modelVersionId": 1,
                                        "modelName": "word2vec:1",
                                        "runtimeName": "hydrosphere/serving-runtime-spark"
                                    },
                                    "weight": 50,
                                    "signature": "signature_name: \"default_spark\"\ninputs {\n  field_name: \"text\"\n  info {\n    dtype: DT_STRING\n    tensor_shape {\n      dim {\n        size: -1\n        name: \"\"\n      }\n      unknown_rank: false\n    }\n  }\n}\noutputs {\n  field_name: \"result\"\n  info {\n    dtype: DT_DOUBLE\n    tensor_shape {\n      dim {\n        size: 3\n        name: \"\"\n      }\n      unknown_rank: false\n    }\n  }\n}\n"
                                },
                                {
                                    "serviceDescription": {
                                        "runtimeId": 2,
                                        "modelVersionId": 2,
                                        "modelName": "word2vec:2",
                                        "runtimeName": "hydrosphere/serving-runtime-spark"
                                    },
                                    "weight": 50,
                                    "signature": "signature_name: \"default_spark\"\ninputs {\n  field_name: \"text\"\n  info {\n    dtype: DT_STRING\n    tensor_shape {\n      dim {\n        size: -1\n        name: \"\"\n      }\n      unknown_rank: false\n    }\n  }\n}\noutputs {\n  field_name: \"result\"\n  info {\n    dtype: DT_DOUBLE\n    tensor_shape {\n      dim {\n        size: 3\n        name: \"\"\n      }\n      unknown_rank: false\n    }\n  }\n}\n"
                                }
                            ],
                            "signature": "signature_name: \"0\"\ninputs {\n  field_name: \"text\"\n  info {\n    dtype: DT_STRING\n    tensor_shape {\n      dim {\n        size: -1\n        name: \"\"\n      }\n      unknown_rank: false\n    }\n  }\n}\noutputs {\n  field_name: \"result\"\n  info {\n    dtype: DT_DOUBLE\n    tensor_shape {\n      dim {\n        size: 3\n        name: \"\"\n      }\n      unknown_rank: false\n    }\n  }\n}\n"
                        }
                    ]
                },
                "contract": "model_name: \"weighted_application\"\nsignatures {\n  signature_name: \"weighted_application\"\n  inputs {\n    field_name: \"text\"\n    info {\n      dtype: DT_STRING\n      tensor_shape {\n        dim {\n          size: -1\n          name: \"\"\n        }\n        unknown_rank: false\n      }\n    }\n  }\n  outputs {\n    field_name: \"result\"\n    info {\n      dtype: DT_DOUBLE\n      tensor_shape {\n        dim {\n          size: 3\n          name: \"\"\n        }\n        unknown_rank: false\n      }\n    }\n  }\n}\n"
            },
            {
                "name": "databricks_w2v",
                "kafkaStreaming": [],
                "id": 4,
                "executionGraph": {
                    "stages": [
                        {
                            "services": [
                                {
                                    "serviceDescription": {
                                        "runtimeId": 3,
                                        "modelVersionId": 5,
                                        "modelName": "word2vecnew:1",
                                        "runtimeName": "hydrosphere/serving-runtime-spark"
                                    },
                                    "weight": 100
                                }
                            ]
                        }
                    ]
                },
                "contract": "model_name: \"word2vecnew\"\nsignatures {\n  signature_name: \"default_spark\"\n  inputs {\n    field_name: \"text\"\n    info {\n      dtype: DT_STRING\n      tensor_shape {\n        dim {\n          size: -1\n          name: \"\"\n        }\n        unknown_rank: false\n      }\n    }\n  }\n  outputs {\n    field_name: \"result\"\n    info {\n      dtype: DT_DOUBLE\n      tensor_shape {\n        dim {\n          size: 3\n          name: \"\"\n        }\n        unknown_rank: false\n      }\n    }\n  }\n}\n"
            },
            {
                "name": "ssd_app",
                "kafkaStreaming": [],
                "id": 3,
                "executionGraph": {
                    "stages": [
                        {
                            "services": [
                                {
                                    "serviceDescription": {
                                        "runtimeId": 5,
                                        "modelVersionId": 4,
                                        "modelName": "ssd_model_example:2",
                                        "runtimeName": "hydrosphere/serving-runtime-python"
                                    },
                                    "weight": 100
                                }
                            ]
                        }
                    ]
                },
                "contract": "model_name: \"\"\n"
            }
        ]
