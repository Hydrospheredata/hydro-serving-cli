import unittest
import os

from hydroserving.parsers.application import ApplicationParser

FILES_PATH = os.path.abspath('./examples/full-apply-example')


class TestApplicationFile(unittest.TestCase):
    def test_simple_app(self):
        app_parser = ApplicationParser()
        app = app_parser.parse_yaml(os.path.join(FILES_PATH, '6-claims-app.yml'))
        print(app)
        self.assertIsNotNone(app)

    def test_pipeline_app(self):
        app_parser = ApplicationParser()
        app = app_parser.parse_yaml(os.path.join(FILES_PATH, '7-claims-pipeline-app.yml'))
        print(app)
        self.assertIsNotNone(app)
