
from typing import List, Dict
from hydrosdk.cluster import Cluster
from hydrosdk.servable import Servable


class ServableService:
    def __init__(self, cluster: Cluster):
        self.cluster = cluster

    def list(self) -> List[Servable]:
        """
        List all Servables on the cluster.

        :return: list of Servable instances
        """
        return Servable.list(self.cluster)

    def create(self, name: str, version: int, metadata: Dict[str, str] = None, deployment_configuration: str = None) -> Servable:
        """
        Deploy an instance of the uploaded model version on the cluster (Servable).

        :param name: a name of the model
        :param version: a version of the model
        :param metadata: a metadata to be assigned to the Servable
        :param deployment_configuration: a DeploymentConfiguration name to be used for to deploy a Servable
        :return: a Servable instance
        """
        return Servable.create(self.cluster, name, version, metadata, deployment_configuration)

    def delete(self, name: str) -> dict:
        """
        Delete a Servable instance.

        :param name: name of the servable
        :return: json response from the cluster
        """
        return Servable.delete(self.cluster, name)

    def find(self, name: str) -> Servable:
        """
        Search for a Servable with a given name.

        :param name: a name of the servable
        :return: a Servable instance
        """
        return Servable.find_by_name(self.cluster, name)

    def logs(self, name: str, follow: bool = False):
        return self.find(name).logs(follow)
