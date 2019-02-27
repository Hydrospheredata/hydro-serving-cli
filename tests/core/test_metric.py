from hydroserving.core.monitoring.parser import metric_spec_config_factory


def test_metric_factory():
    res = metric_spec_config_factory("KSMetricSpec", input="in")
    print(res)
    assert res['input'] == 'in'
