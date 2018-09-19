from hydroserving.httpclient.remote_connection import RemoteConnection

"""
        {
          "filter": {
            "sourceName": "client_profile",
            "stageId": "app1stage0"
          },
          "name": "auto2",
          "metricProviderSpecification": {
            "metricProviderClass": "io.hydrosphere.sonar.core.metrics.providers.Autoencoder",
            "config": {
              "applicationId": 1
            },
            "withHealth": true,
            "healthConfig": {
              "threshold": "17"
            }
          }
        }
"""

METRIC_PROVIDERS = {
    "autoencoder": "io.hydrosphere.sonar.core.metrics.providers.Autoencoder",
    "kolmogorov-smirnov": "io.hydrosphere.sonar.core.metrics.providers.KolmogorovSmirnov",
    "random-forest": "io.hydrosphere.sonar.core.metrics.providers.RandomForest",
    "gan": "io.hydrosphere.sonar.core.metrics.providers.GAN"
}


class HealthConfigSpecification:
    def __init__(self, threshold):
        """

        Args:
            threshold (int):
        """
        self.threshold = threshold


class MetricConfigSpecification:
    def __init__(self, application_id):
        """

        Args:
            application_id (str):
        """
        self.applicationId = application_id


class MetricProviderSpecification:
    def __init__(self, metric_provider_class, config, with_health, health_config):
        """

        Args:
            health_config (HealthConfigSpecification or None):
            with_health (bool or None):
            config (MetricConfigSpecification or None):
            metric_provider_class (str):
        """
        self.healthConfig = health_config
        self.withHealth = with_health
        self.config = config
        self.metricProviderClass = metric_provider_class


class FilterSpecification:
    def __init__(self, source_name, stage_id):
        """

        Args:
            stage_id (str):
            source_name (str):
        """
        self.stageId = stage_id
        self.sourceName = source_name


class EntryAggregationSpecification:
    def __init__(self, name, metric_provider_specification, filter):
        """

        Args:
            name (str):
            filter (FilterSpecification):
            metric_provider_specification (MetricProviderSpecification):
        """
        self.filter = filter
        self.metricProviderSpecification = metric_provider_specification
        self.name = name


class MonitoringAPI:
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
