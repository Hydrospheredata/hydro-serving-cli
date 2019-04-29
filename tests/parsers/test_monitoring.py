import unittest
import json

import yaml

from hydroserving.core.monitoring.parser import parse_monitoring_params


class MonitoringParserSpec(unittest.TestCase):
    def test_health_flag(self):
        # name: Latency
        # kind: LatencyMetricSpec
        # with-health: false
        # config:
        # “interval”: 15
        yaml_doc = """
        monitoring:
          - name: Latency
            kind: LatencyMetricSpec
            with-health: true
            config:
              interval: 15
              threshold: 10
        """
        monitoring_config = yaml.load(yaml_doc)['monitoring']
        result = parse_monitoring_params(monitoring_config)
        print(json.dumps(result[0]))
        self.assertTrue(result[0]['withHealth'])
        self.assertEqual(result[0]['config']['threshold'], 10)

    def test_custom_metric(self):
        yaml_doc = """
        monitoring:
          - name: TestMetric
            kind: Accuracy
            with-health: true
        """
        monitoring_config = yaml.load(yaml_doc)['monitoring']
        result = parse_monitoring_params(monitoring_config)
        print(json.dumps(result[0]))
        self.assertTrue(result[0]['withHealth'])
        self.assertFalse("threshold" in result[0]['config'])
