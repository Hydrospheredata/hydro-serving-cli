from typing import List

from hydrosdk.cluster import Cluster
from hydrosdk.deployment_configuration import (
    DeploymentConfiguration, DeploymentConfigurationBuilder,
)


class DeploymentConfigurationService:
    def __init__(self, cluster: Cluster):
        self.cluster = cluster

    def find(self, name: str) -> DeploymentConfiguration:
        """
        Search a deployment configuration by name

        :param name: name of the deployment configuration
        :return: DeploymentConfiguration instance
        """
        return DeploymentConfiguration.find(self.cluster, name)

    def apply(self, builder: DeploymentConfigurationBuilder) -> DeploymentConfiguration:
        """
        Create a DeploymentConfiguration on the cluster
        
        :param builder: an instance of the DeploymentConfigurationBuilder with all required attributes
        :return: DeploymentConfiguration instance
        """
        return builder.build()

    def delete(self, name: str) -> dict:
        """
        Delete deployment configuration from the cluster

        :param name: name of the deployment configuration
        :return: json response from the cluster
        """
        return DeploymentConfiguration.delete(self.cluster, name)

    def list(self) -> List[DeploymentConfiguration]:
        """
        List all deployment configurations

        :return: list of DeploymentConfiguration instances
        """
        return DeploymentConfiguration.list(self.cluster)
