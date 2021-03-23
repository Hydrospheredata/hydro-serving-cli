import logging
import functools
import copy
from typing import List, Dict, Callable, Tuple

from click import ClickException

from hydroserving.core.monitoring.parser import parse_monitoring_params

from hydrosdk.modelversion import LocalModel, MonitoringConfiguration
from hydrosdk.signature import ModelSignature, signature_dict_to_ModelSignature
from hydrosdk.monitoring import MetricSpecConfig
from hydrosdk.image import DockerImage
from hydrosdk.cluster import Cluster


def _fill_model(
        name: str, 
        runtime: DockerImage, 
        payload: List[str], 
        signature: ModelSignature,
        metadata: Dict[str, str],
        install_command: str,
        training_data: str,
        monitoring_configuration: MonitoringConfiguration,
        metrics: List[Callable[[Cluster], Tuple[str, MetricSpecConfig]]],
        path: str
) -> Tuple[LocalModel, List[Callable[[Cluster], Tuple[str, MetricSpecConfig]]]]:
    """Used to partially apply arguments."""
    return (LocalModel(
        name, 
        runtime, 
        path, 
        payload, 
        signature, 
        metadata, 
        install_command, 
        training_data, 
        monitoring_configuration
    ), metrics)


def parse_runtime(value: str) -> DockerImage:
    try: 
        return DockerImage.from_string(value)
    except ValueError as e:
        raise ClickException("Invalid runtime image") from e


def parse_model(in_dict: dict) -> \
    Callable[[str], Tuple[LocalModel, List[Callable[[Cluster], Tuple[str, MetricSpecConfig]]]]]:
    """
    Parse a model definition from the json/yaml description.

    :param in_dict: definition of the model
    :return: a LocalModel instance

    :example:

    kind: Model
    name: "my-model"
    payload:
      - "src/"
      - "requirements.txt"
    runtime: "hydrosphere/serving-runtime-python-3.8:latest"
    training-data: "s3://bucket/object.csv"
    metadata:
      author: myself
      owner: myself
      contributor: myself
      distributor: myself
      appreciator: myself
    signature:
      name: "infer"
      inputs:
        x:
          shape: [112]
          type: "float64"
          profile: "numerical"
      outputs:
        y:
          shape: "scalar"
          type: "int64"
          profile: "numerical"
    monitoring:
      configuration:
        batchSize: 100
      metrics:
        - name: "custom-metric"
          config:
            monitoring-model: "custom-metric-for-my-model:1"
            threshold: 12
            operator: "<="
    """
    try:
        name = in_dict["name"]
    except KeyError as e:
        raise ClickException("'name' field is not defined or invalid") from e

    try: 
        raw_runtime = in_dict["runtime"]
        runtime = parse_runtime(raw_runtime)
    except KeyError as e:
        raise ClickException("'runtime' field is not defined or invalid") from e

    try:
        payload = in_dict["payload"]
    except KeyError as e:
        raise ClickException("'payload' field is not defined or invalid") from e

    try:
        raw_signature = copy.deepcopy(in_dict["signature"])
        raw_signature["signatureName"] = raw_signature["name"]
        raw_signature["inputs"] = prepare_fields(raw_signature["inputs"])
        raw_signature["outputs"] = prepare_fields(raw_signature["outputs"])
        del raw_signature["name"]
        signature = signature_dict_to_ModelSignature(raw_signature)
    except KeyError as e:
        raise ClickException("'signature' field is not defined or invalid") from e

    metadata = parse_metadata(in_dict.get("metadata"))
    install_command = in_dict.get("install-command")
    training_data = in_dict.get("training-data")
    (monitoring_configuration, metrics) = parse_monitoring_params(in_dict.get("monitoring", {}))
    return functools.partial(
        _fill_model,
        name,
        runtime,
        payload,
        signature,
        metadata,
        install_command,
        training_data,
        monitoring_configuration,
        metrics,
    )


def parse_metadata(in_dict) -> Dict[str, str]:
    if in_dict is None:
        return {}
    res = {}
    for key, val in in_dict.items():
        if not isinstance(val, str):
            res[key] = str(val)
        else:
            res[key] = val
    return res


def prepare_fields(in_dict):
    return [dict(name=name, **values) for name, values in in_dict.items()]
