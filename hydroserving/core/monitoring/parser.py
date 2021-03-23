import functools
from typing import Union, Tuple, List, Callable

from click import ClickException

from hydrosdk.monitoring import MetricSpecConfig, ThresholdCmpOp
from hydrosdk.cluster import Cluster
from hydrosdk.modelversion import ModelVersion, MonitoringConfiguration


ThresholdOpToStr = {
    "==": ThresholdCmpOp.EQ,
    "!=": ThresholdCmpOp.NOT_EQ,
    ">": ThresholdCmpOp.GREATER,
    "<": ThresholdCmpOp.LESS,
    ">=": ThresholdCmpOp.GREATER_EQ,
    "<=": ThresholdCmpOp.LESS_EQ,
}


def _fill_metric_spec(
        metric_name: str, 
        mv_name: str, 
        mv_version: int, 
        threshold: Union[int, float], 
        operator: str,
        cluster: Cluster, 
) -> Tuple[str, MetricSpecConfig]:
    """
    Create a MetricSpecConfig for the specified ModelVersion.

    :param metric_name: a name of the metric
    :param mv_name: a name of the ModelVersion, which will be used as a metric
    :param mv_version: a version of the ModelVersion, which will be used as a metric
    :param threshold: a threshold for the metric
    :param operator: operator to be used to compare metric values against a threshold
    :param cluster: a Cluster instance
    :return: tuple of metric name and metric spec
    """
    mv = ModelVersion.find(cluster, mv_name, mv_version)
    thresholdCmpOp = ThresholdOpToStr.get(operator)
    if not thresholdCmpOp:
        raise TypeError(f"Invalid comparison operator: {operator}")
    return (metric_name, MetricSpecConfig(mv.id, threshold, thresholdCmpOp))
    

def parse_monitoring_params(in_dict: dict) -> \
        Tuple[MonitoringConfiguration, List[Callable[[Cluster], Tuple[str, MetricSpecConfig]]]]:
    """
    Return a parsed definition of the monitoring section of the model.

    :param in_dict: 
    :return:

    :example:
    
    batchSize: 100
    metrics:
    - name: "custom-metric"
      config:
        monitoring-model: "custom-metric-for-my-model:1"
        threshold: 12
        operator: "<="
    """
    almost_metrics = []
    for metric in in_dict.get("metrics", []):
        metric_name = metric["name"]
        try:
            name, version = metric["config"]["monitoring-model"].split(':')
        except ValueError as e:
            raise ClickException(f"Invalid metric specification: {metric_name}") from e
        almost_metrics.append(functools.partial(
            _fill_metric_spec, 
            metric_name,
            name,
            version,
            metric["threshold"],
            metric["operator"]
        ))
    
    return (
        MonitoringConfiguration(in_dict.get("batchSize", 100)), 
        almost_metrics, 
    )

