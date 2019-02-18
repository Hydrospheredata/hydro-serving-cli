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

    def create_aggregation(self, create_request):
        """

        Args:
            create_request (EntryAggregationSpecification):
        """
        return self.connection.post("/monitoring/aggregations", create_request)

    def delete_aggregation(self, aggregation_id):
        """

        Args:
            aggregation_id (str):
        """
        return self.connection.delete("/monitoring/aggregations/" + aggregation_id)

    def list_aggregations(self):
        return self.connection.get("/monitoring/aggregations")
