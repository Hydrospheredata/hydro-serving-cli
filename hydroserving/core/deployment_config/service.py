from hydrosdk.cluster import Cluster
from hydrosdk.deployment_configuration import DeploymentConfiguration

from hydroserving.http.remote_connection import RemoteConnection


class DeploymentConfigurationService:
    def __init__(self, connection: RemoteConnection):
        self.connection = connection
        self.cluster = Cluster(self.connection.remote_addr)

    def get(self, deployment_configuration_name):
        return DeploymentConfiguration.find(self.cluster, deployment_configuration_name)

    def apply(self, deployment_configuration: DeploymentConfiguration):
        data = deployment_configuration.to_camel_case_dict()
        self.connection.post_json("/api/v2/deployment_configuration", data)

    def delete(self, deployment_configuration_name):
        return DeploymentConfiguration.delete(self.cluster, deployment_configuration_name)

    def list(self):
        return DeploymentConfiguration.list(self.cluster)
