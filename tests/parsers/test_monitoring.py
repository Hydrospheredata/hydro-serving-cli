import unittest
import json

import yaml

from hydroserving.core.monitoring.service import parse_monitoring_params


class MonitoringParserSpec(unittest.TestCase):
    def test_correct_custom_metric(self):
        yaml_doc = """
        monitoring:
          - name: TestMetric
            config: 
              monitoring-model: adult-scalar:12
              operator: "<="
              threshold: 0.7
        """
        monitoring_config = yaml.load(yaml_doc)['monitoring']
        result = parse_monitoring_params(monitoring_config)
        print(json.dumps(result[0]))
        self.assertEqual(
            set(result[0]['config'].keys()),
            {'monitoringModelVersion', 'monitoringModelName', 'thresholdCmpOperator', 'threshold'}
        )

    @unittest.expectedFailure
    def test_incorrect_name_custom_metric(self):
        yaml_doc = """
        monitoring:
          - name: TestMetric
            config: 
              monitoring-model: adult-scalar
              operator: "<="
              threshold: 0.7
        """
        monitoring_config = yaml.load(yaml_doc)['monitoring']
        result = parse_monitoring_params(monitoring_config)