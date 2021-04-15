import logging
import functools
import copy
import os
import json
from typing import List, Dict, Callable, Tuple, Optional
from google.protobuf.json_format import MessageToJson

from click import ClickException

from hydroserving.util.parseutil import fill_arguments
from hydroserving.core.model.package import enrich_and_normalize, assemble_model_on_local_fs
from hydroserving.util.parseutil import _parse_model_reference
from hydroserving.core.apply.context import ApplyContext

from hydrosdk.modelversion import ModelVersion, ModelVersionBuilder, MonitoringConfiguration
from hydrosdk.signature import ModelSignature, signature_dict_to_ModelSignature
from hydrosdk.monitoring import MetricSpecConfig, ThresholdCmpOp
from hydrosdk.image import DockerImage
from hydrosdk.cluster import Cluster
from hydrosdk.builder import AbstractBuilder


def parse_model(in_dict: dict) -> Callable[[Cluster], ModelVersion]:
    """
    Parse a model definition from the json/yaml description.

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
    class LocalBuilder(AbstractBuilder):
        def __init__(self, in_dict: dict):
            self.in_dict = in_dict
        
        def build(self, cluster: Cluster, **kwargs) -> ModelVersion:
            apply_context: ApplyContext = kwargs.get("apply_context", ApplyContext())
            logging.debug(f"Apply context: {apply_context.to_dict()}")

            path: str = kwargs.get("path")
            if path is None:
                path = os.getcwd()
                logging.warning(f"Path was not provided, using current directory: {path}")

            builder = ModelVersionBuilder(_parse_name(self.in_dict), path, self.in_dict.get('source-path')) \
                .with_signature(_parse_signature(self.in_dict)) \
                .with_runtime(_parse_runtime(self.in_dict)) \
                .with_monitoring_configuration(_parse_monitoring_configuration(self.in_dict.get('monitoring', {}))) \
                .with_metadata(_parse_metadata(self.in_dict))
            payload = _parse_payload(self.in_dict)
            if payload:
                builder.with_payload(payload)
            builder = enrich_and_normalize(builder)
            _ = assemble_model_on_local_fs(builder)
            install_command = self.in_dict.get("install-command")
            if install_command:
                builder.with_install_command(install_command)
            training_data = self.in_dict.get("training-data")
            if training_data:
                builder.with_training_data(training_data)
            return builder.build(cluster)
    
    return functools.partial(
        fill_arguments,
        lambda **kwargs: LocalBuilder(in_dict),
    )


def parse_metrics(in_dict: dict) -> Callable[[Cluster], List[Tuple[str, MetricSpecConfig]]]:
    """
    Parse metrics from json/yaml format.

    metrics:
      - name: "custom-metric"
        config:
          monitoring-model: "custom-metric-for-my-model:1"
          threshold: 12
          operator: "<="
    """
    class LocalBuilder(AbstractBuilder):
        ThresholdOpToStr = {
            "==": ThresholdCmpOp.EQ,
            "!=": ThresholdCmpOp.NOT_EQ,
            ">": ThresholdCmpOp.GREATER,
            "<": ThresholdCmpOp.LESS,
            ">=": ThresholdCmpOp.GREATER_EQ,
            "<=": ThresholdCmpOp.LESS_EQ,
        }

        def __init__(self, in_dict: dict) -> 'LocalBuilder':
            self.metrics = []
            self.in_dict = in_dict

        def build(self, cluster: Cluster, **kwargs) -> List[Tuple[str, MetricSpecConfig]]:
            for metric in self.in_dict.get("metrics", []):
                metric_name = metric["name"]
                reference = metric["config"]["monitoring-model"]
                model_version = apply_context.parse_model_version(reference)
                if model_version is None:
                    name, version = _parse_model_reference(reference)
                    model_version = ModelVersion.find(cluster, name, version)
                operator = ThresholdOpToStr.get(metric["operator"])
                if not operator:
                    raise TypeError(f"Invalid or undefined comparison operator: {operator}")
                threshold = metric.get("threshold")
                if not thresholdCmpOp:
                    raise TypeError(f"Undefined threshold: {threshold}")
                
                self.metrics.append((
                    metric_name, 
                    MetricSpecConfig(model_version.id, threshold, operator)
                ))
            return self.metrics

    return functools.partial(
        fill_arguments, 
        lambda **kwargs: LocalBuilder(in_dict),
    )


def _parse_monitoring_configuration(in_dict: dict) -> MonitoringConfiguration:
    logging.debug(f"Parsing monitoring configuration")
    config = None
    if in_dict.get('configuration') is None:
        logging.warning("Couldn't find monitoring configuration, applying defaults")
        config = MonitoringConfiguration(batch_size=100)
    else: 
        config = MonitoringConfiguration(
            batch_size=_parse_batch_size(in_dict['configuration'])
        )
    logging.debug(f"Parsed monitoring configuration: {json.dumps(config.to_dict())}")
    return config


def _parse_batch_size(in_dict: dict) -> int:
    logging.debug(f"Parsing batch size")
    batch_size = None
    if in_dict.get("batch-size") is None:
        logging.warning("Couldn't find batch size, setting default")
        batch_size = 100
    else: 
        batch_size = in_dict["batch-size"]
    logging.debug(f"Parsed batch size: {batch_size}")
    return batch_size


def _parse_signature(in_dict: dict) -> ModelSignature:
    logging.debug(f"Parsing signature: {in_dict.get('signature')}")
    if in_dict.get('signature') is None:
        logging.error("Couldn't find signature field")
        raise SystemExit(1)
    raw_signature = copy.deepcopy(in_dict["signature"])
    raw_signature["signatureName"] = raw_signature["name"]
    raw_signature["inputs"] = _parse_fields(raw_signature["inputs"])
    raw_signature["outputs"] = _parse_fields(raw_signature["outputs"])
    del raw_signature["name"]
    signature = signature_dict_to_ModelSignature(raw_signature)
    logging.debug(f"Parsed signature: {MessageToJson(signature)}")
    return signature


def _parse_training_data(training_path: str, source_path: str) -> str:
    if training_path.startswith("s3://"):
        return training_path
    else:
        return os.path.join(source_path, training_path)


def _parse_runtime(in_dict: dict) -> DockerImage:
    logging.debug(f"Parsing runtime")
    if in_dict.get('runtime') is None:
        logging.error("Couldn't find runtime field")
        raise SystemExit(1)
    runtime = DockerImage.from_string(in_dict['runtime'])
    logging.debug(f"Parsed runtime: {runtime.to_string()}")
    return runtime


def _parse_name(in_dict: dict) -> str:
    logging.debug(f"Parsing name")
    if in_dict.get('name') is None:
        logging.error("Couldn't find name field")
        raise SystemExit(1)
    name = in_dict["name"]
    logging.debug(f"Parsed name: {name}")
    return name


def _parse_payload(in_dict: dict) -> Optional[List[str]]:
    logging.debug(f"Parsing payload")
    if in_dict.get('payload') is None:
        logging.error("Couldn't find payload field")
        return None
    payload = in_dict["payload"]
    logging.debug(f"Parsed payload: {payload}")
    return payload


def _parse_metadata(in_dict: dict) -> Dict[str, str]:
    logging.debug(f"Parsing metadata")
    res = in_dict.get('metadata', {})
    for key, val in res.items():
        if not isinstance(val, str):
            res[key] = str(val)
        else:
            res[key] = val
    if res:
        logging.debug(f"Parsed metadata: {res}")
    else:
        logging.debug("Couldn't find any metadata")
    return res


def _parse_fields(in_dict):
    return [dict(name=name, **values) for name, values in in_dict.items()]
