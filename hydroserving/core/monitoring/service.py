import logging
from enum import Enum

from hydroserving.util.fileutil import read_in_chunks


class DataProfileStatus(Enum):
    Success = "Success"
    Failure = "Failure"
    Processing = "Processing"
    NotRegistered = "NotRegistered"


def custom_model_metric_spec(monitoring_model, threshold, threshold_op):
    if not isinstance(monitoring_model, str):
        raise TypeError("Invalid monitoring_model: {}".format(monitoring_model))

    try:
        name, version = monitoring_model.split(":")
    except ValueError:
        raise ValueError("Invalid model identifier. Expected format {name}:{version}")

    allowed = {
        "==": "Eq",
        "!=": "NotEq",
        ">": "Greater",
        "<": "Less",
        ">=": "GreaterEq",
        "<=": "LessEq",
    }

    if not isinstance(threshold_op, str):
        raise TypeError("Invalid comparison operator type: {}".format(type(threshold_op)))

    value = allowed.get(threshold_op)
    if not value:
        if value not in allowed.values():
            raise TypeError("Invalid comparison operator: {}".format(threshold_op))
        else:
            value = threshold_op

    return {
        "monitoringModelName": name,
        "monitoringModelVersion": version,
        "thresholdCmpOperator": {
            "kind": value
        },
        "threshold": float(threshold)
    }

def parse_monitoring_params(in_dict):
    """

    Args:
        in_dict (dict):

    Returns:
        MonitoringParams:
    """
    if in_dict is None:
        return None
    result = []
    for item in in_dict:
        monitoring_model_name = item['config']['monitoring-model']
        threshold = item['config']['threshold']
        threshold_op = item['config']['operator']
        result.append(
            {
                "name": item["name"],
                "config": custom_model_metric_spec(monitoring_model_name, threshold, threshold_op)
            }
        )
    return result



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
