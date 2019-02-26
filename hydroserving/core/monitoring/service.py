import logging
from enum import Enum

from hydroserving.util.fileutil import read_in_chunks


class DataProfileStatus(Enum):
    Success = "Success"
    Failure = "Failure"
    Processing = "Processing"
    NotRegistered = "NotRegistered"


def ks_metric_spec(input):
    if not isinstance(input, str):
        raise TypeError("Invalid input: {}".format(input))
    return {
        "input": input
    }


def rf_metric_spec(input, application, threshold):
    if not isinstance(input, str):
        raise TypeError("Invalid input: {}".format(input))
    if not isinstance(application, str):
        raise TypeError("Invalid app_name: {}".format(application))
    if threshold and not isinstance(threshold, float):
        raise TypeError("Invalid threshold: {}".format(input))
    return {
        "input": input,
        "applicationName": application,
        "threshold": threshold
    }


def ae_metric_spec(input, application, threshold):
    if not isinstance(input, str):
        raise TypeError("Invalid input: {}".format(input))
    if not isinstance(application, str):
        raise TypeError("Invalid app_name: {}".format(application))
    if threshold and not (isinstance(threshold, float) or isinstance(threshold, int)):
        raise TypeError("Invalid threshold: {}".format(threshold))
    return {
        "input": input,
        "applicationName": application,
        "threshold": threshold
    }


def gan_metric_spec(input, application):
    if not isinstance(input, str):
        raise TypeError("Invalid input: {}".format(input))
    if not isinstance(application, str):
        raise TypeError("Invalid app_name: {}".format(application))
    return {
        "input": input,
        "applicationName": application,
    }


def latency_metric_spec(interval, threshold):
    if not isinstance(interval, int):
        raise TypeError("Invalid interval: {}".format(interval))
    if threshold and not isinstance(threshold, float):
        raise TypeError("Invalid threshold: {}".format(threshold))
    return {
        "interval": interval,
        "threshold": threshold
    }


def counter_metric_spec(interval):
    if not isinstance(interval, int):
        raise TypeError("Invalid interval: {}".format(interval))
    return {
        "interval": interval
    }


def error_rate_metric_spec(interval, threshold):
    if not isinstance(interval, int):
        raise TypeError("Invalid interval: {}".format(interval))
    if threshold and not isinstance(threshold, float):
        raise TypeError("Invalid threshold: {}".format(threshold))
    return {
        "interval": interval,
        "threshold": threshold
    }


METRIC_KINDS = {
    "KSMetricSpec": ks_metric_spec,
    "RFMetricSpec": rf_metric_spec,
    "AEMetricSpec": ae_metric_spec,
    "GANMetricSpec": gan_metric_spec,
    "LatencyMetricSpec": latency_metric_spec,
    "CounterMetricSpec": counter_metric_spec,
    "ErrorRateMetricSpec": error_rate_metric_spec
}


def metric_spec_config_factory(kind, **kwargs):
    ctor = METRIC_KINDS.get(kind, None)
    if ctor:
        if kwargs:
            try:
                return ctor(**kwargs)
            except Exception as ex:
                raise ValueError("Invalid '{}' config: {}".format(kind, ex))
        raise ValueError("No metric spec args provided")
    raise ValueError("Unknown metric spec kind: {}".format(kind))


def metric_spec_factory(name, model_version_id, with_health, kind, **config_args):
    config = metric_spec_config_factory(kind, **config_args)
    return {
        "name": name,
        "modelVersionId": model_version_id,
        "config": config,
        "withHealth": with_health,
        "kind": kind
    }


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
        return self.connection.post_json("/monitoring/metricspec", create_request).json()

    def list_metric_specs(self):
        return self.connection.get("/monitoring/metricspec").json()

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
