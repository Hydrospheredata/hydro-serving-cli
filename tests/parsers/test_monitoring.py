import unittest
import json
from hydroserving.core.monitoring.parser import parse_monitoring_params


class MonitoringParserSpec(unittest.TestCase):
    def test_health_flag(self):
        # name: Latency
        # kind: LatencyMetricSpec
        # with-health: false
        # config:
        # “interval”: 15
        monitoring_config = [{
            "name": "Latency",
            "kind": "LatencyMetricSpec",
            "with-health": True,
            "config": {
                "interval": 15
            }
        }]
        result = parse_monitoring_params(monitoring_config)
        print(result)
        print(json.dumps(result))
        self.assertTrue(result[0]['withHealth'])
        self.assertFalse("threshold" in result[0]['config'])
