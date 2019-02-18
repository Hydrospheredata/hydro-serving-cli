import unittest
import os
from hydroserving.util.yamlutil import yaml_file
from hydroserving.core.application.parser import parse_application

FILES_PATH = os.path.abspath('./examples/full-apply-example')


class TestApplicationFile(unittest.TestCase):
    def test_simple_app(self):
        with open(os.path.join(FILES_PATH, '5-claims-app.yml')) as f:
            d = yaml_file(f)
        print(d)
        app = parse_application(d)
        print(app)
        self.assertIsNotNone(app)

    def test_pipeline_app(self):
        with open(os.path.join(FILES_PATH, '6-claims-pipeline-app.yml')) as f:
            d = yaml_file(f)
        print(d)
        app = parse_application(d)
        print(app)
        self.assertIsNotNone(app)
