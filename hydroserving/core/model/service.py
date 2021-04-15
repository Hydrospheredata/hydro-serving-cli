import json
import logging
import itertools
from typing import List, Iterable, Callable, Tuple, Optional
from copy import deepcopy

from hydrosdk.cluster import Cluster
from hydrosdk.modelversion import ModelVersion, ModelVersionBuilder
from hydrosdk.monitoring import MetricSpecConfig, MetricSpec
from hydrosdk.utils import handle_request_error
from hydrosdk.exceptions import BadRequestException
from sseclient import Event

from hydroserving.util.err_handler import handle_cluster_error
from hydroserving.core.apply.context import ApplyContext


class ModelService:

    def __init__(self, cluster: Cluster):
        self.cluster = cluster

    @handle_cluster_error
    def get_build_logs(self, model_version_id: str) -> Iterable[Event]:
        """
        Retrieve build logs for the model version.

        :return: Iterator over sseclient.Event
        """
        mv = ModelVersion.find_by_id(self.cluster, model_version_id)
        return mv.build_logs()

    @handle_cluster_error
    def list_models(self) -> dict:
        resp = self.cluster.request("GET", f"{ModelVersion._BASE_URL}")
        handle_request_error(
            resp, f"Failed to list models versions. {resp.status_code} {resp.text}")
        return resp.json()

    @handle_cluster_error
    def list_models_enriched(self) -> Iterable[Tuple[int, str, Iterable[ModelVersion]]]:
        """
        List all models on the cluster.

        :return: list of model names
        """
        id_mapping = {item["name"] : item["id"] for item in self.list_models()}
        mvs = ModelVersion.list(self.cluster)
        for name, versions in itertools.groupby(mvs, key=lambda x: x.name):
            yield id_mapping[name], name, versions
    
    @handle_cluster_error
    def list_versions(self) -> List[ModelVersion]:
        """
        List all model versions on the cluster.

        :return: list of ModelVersion instances
        """
        return ModelVersion.list(self.cluster)
    
    @handle_cluster_error
    def list_versions_by_model_name(self, model_name: str) -> List[ModelVersion]:
        """
        List model versions for the defined model on the cluster.

        :return: list of ModelVersion instances
        """
        return ModelVersion.find_by_model_name(self.cluster, model_name)
    
    @handle_cluster_error
    def list_versions_by_model_id(self, model_id: int) -> List[ModelVersion]:
        """
        List model versions for the defined model on the cluster.

        :return: list of ModelVersion instances
        """
        for id_, _, versions in self.list_models_enriched():
            if id_ == model_id:
                return list(versions)
        raise BadRequestException(f"Couldn't find model versions for the given model_id={model_id}")

    @handle_cluster_error
    def find_version(self, model_name: str, model_version: int) -> ModelVersion:
        """
        Find a ModelVersion on the cluster by model name and a version.

        :param model_name: name of the model
        :param model_version: version of the model
        :return: ModelVersion instance
        """
        return ModelVersion.find(self.cluster, model_name, model_version)
    
    @handle_cluster_error
    def find_version_by_id(self, id_: int) -> ModelVersion:
        """
        Find a ModelVersion on the cluster by id.

        :param id_: unique id of the model
        :return: ModelVersion instance
        """
        return ModelVersion.find_by_id(self.cluster, id_)

    @handle_cluster_error
    def find_model_by_name(self, name: str) -> int:
        """
        Find a Model on the cluster by its name.

        :param name: name of the model
        :return: id of the model (not model version id)
        """
        for model_json in self.list_models():
            if model_json.get("name") == name:
                return model_json["id"]
        raise BadRequestException(f"Failed to find the model with a name {name}.")
    
    @handle_cluster_error
    def apply(self, 
            partial_model_parser: Callable[[Cluster, str], ModelVersion],
            partial_metric_parser: Callable[[Cluster], List[Tuple[str, MetricSpecConfig]]],
            path: str,
            apply_context: ApplyContext,
            ignore_training_data: bool,
            ignore_metrics: bool,
            is_async: Optional[bool] = False,
            timeout: Optional[int] = 120,
    ) -> ModelVersion:
        logging.info(f"Parsing and assembling a model at {path}")
        model_version = partial_model_parser(self.cluster, path=path)
        logging.info(f"Submitted model registration request")

        if model_version.training_data:
            if ignore_training_data:
                logging.warning("Ignoring training data upload")
            else:
                logging.info("Submitting training data")
                dur = model_version.upload_training_data()
                if not is_async:
                    logging.info("Waiting for the profiling job to complete")
                    dur.wait()
        
        if ignore_metrics:
            logging.warning("Ignoring metrics assignment")
        else:
            logging.debug("Preparing possible metrics")
            metrics = partial_metric_parser(self.cluster)
            if metrics:
                logging.info("Assigning metrics to the model")
                for metric_name, metric_config in metrics:
                    MetricSpec.create(self.cluster, metric_name, model_version.id, metric_config)
        
        if not is_async:
            logging.info(f"Waiting for the model version to build, timeout set to {timeout} seconds")
            model_version.lock_till_released(timeout)
            logging.info("Build logs:")
            for log in model_version.build_logs():
                logging.info(log.data)
        return model_version
    
    @handle_cluster_error
    def delete(self, model_id: int) -> dict:
        resp = self.cluster.request("DELETE", f"{ModelVersion._BASE_URL}/{model_id}")
        handle_request_error(
            resp, f"Failed to delete a model with model_id={model_id}. {resp.status_code} {resp.text}")
        return resp.json()
