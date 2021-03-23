import logging
from enum import Enum
from typing import Dict, Optional, Tuple, Union, List, Callable

from hydrosdk import Cluster, MetricSpecConfig, ModelVersion
from hydrosdk.monitoring import ThresholdCmpOp

from hydroserving.util.fileutil import read_in_chunks

class DataProfileStatus(Enum):
    Success = "Success"
    Failure = "Failure"
    Processing = "Processing"
    NotRegistered = "NotRegistered"


class MonitoringService:
    def __init__(self, connection):
        """

        Args:
            connection (RemoteConnection):
        """
        self.connection = connection

    def create_metric_spec(self, create_request):
        """

        Args:
            create_request (EntryAggregationSpecification):
        """
        return self.connection.post_json("/api/v2/monitoring/metricspec", create_request).json()

    def list_metric_specs(self):
        return self.connection.get("/api/v2/monitoring/metricspec").json()

    def push_s3_csv(self, model_version_id, s3_path):
        res = self.connection.post_json(
            "/monitoring/profiles/batch/{}".format(model_version_id),
            data={"path": s3_path}
        )
        return res.text  # 200 OK "ok"

    def start_data_processing(self, model_version_id, data_file, chunk_size=420420):
        logging.info("Uploading training data file %s with chunk_size=%s", data_file.name, chunk_size)
        gen = read_in_chunks(data_file, chunk_size=chunk_size)

        res = self.connection.post_stream(
            "/monitoring/profiles/batch/{}".format(model_version_id),
            data=gen
        )
        return res.text  # 200 OK "ok"

    def get_data_processing_status(self, model_version_id):
        res = self.connection.get("/monitoring/profiles/batch/{}/status".format(model_version_id))
        if res.ok:
            d = res.json()
            try:
                status = DataProfileStatus[d["kind"]]
                return status
            except KeyError:
                raise ValueError("Invalid data processing status for modelversion id {}: {}".format(
                    model_version_id, d))
        return None
