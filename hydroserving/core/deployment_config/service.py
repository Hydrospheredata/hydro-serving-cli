import logging

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
        r = self.connection.post_json("/api/v2/deployment_configuration", data)
        if r.ok:
            return f"Successfully uploaded {deployment_configuration}"
        else:
            logging.info(f"Error while uploading {deployment_configuration}:\n\tResponse [{r.status_code}], {r.json()}")
            return f"Failed uploading {deployment_configuration}."

    def delete(self, deployment_configuration_name):
        return DeploymentConfiguration.delete(self.cluster, deployment_configuration_name)

    def list(self):
        return DeploymentConfiguration.list(self.cluster)
