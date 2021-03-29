from typing import List, Callable

from hydrosdk.cluster import Cluster
from hydrosdk.deployment_configuration import DeploymentConfiguration
from hydroserving.util.err_handler import handle_cluster_error


class DeploymentConfigurationService:
    def __init__(self, cluster: Cluster):
        self.cluster = cluster

    @handle_cluster_error
    def find(self, name: str) -> DeploymentConfiguration:
        """
        Search a deployment configuration by name.

        :param name: name of the deployment configuration
        :return: DeploymentConfiguration instance
        """
        return DeploymentConfiguration.find(self.cluster, name)

    @handle_cluster_error
    def apply(self, partial_parser: Callable[[Cluster], DeploymentConfiguration]) -> DeploymentConfiguration:
        """
        Create a DeploymentConfiguration on the cluster.
        
        :param partial_parser: a partial function, which will create a deployment configuration
        :return: DeploymentConfiguration instance
        """
        return partial_parser(self.cluster)

    @handle_cluster_error
    def delete(self, name: str) -> dict:
        """
        Delete deployment configuration from the cluster.

        :param name: name of the deployment configuration
        :return: json response from the cluster
        """
        return DeploymentConfiguration.delete(self.cluster, name)

    @handle_cluster_error
    def list(self) -> List[DeploymentConfiguration]:
        """
        List all deployment configurations.

        :return: list of DeploymentConfiguration instances
        """
        return DeploymentConfiguration.list(self.cluster)
