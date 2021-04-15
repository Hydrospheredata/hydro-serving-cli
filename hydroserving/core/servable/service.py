
from typing import List, Dict
from hydrosdk.cluster import Cluster
from hydrosdk.servable import Servable
from hydroserving.util.err_handler import handle_cluster_error


class ServableService:
    def __init__(self, cluster: Cluster):
        self.cluster = cluster

    @handle_cluster_error
    def list(self) -> List[Servable]:
        """
        List all Servables on the cluster.

        :return: list of Servable instances
        """
        return Servable.list(self.cluster)

    @handle_cluster_error
    def delete(self, name: str) -> dict:
        """
        Delete a Servable instance.

        :param name: name of the servable
        :return: json response from the cluster
        """
        return Servable.delete(self.cluster, name)

    @handle_cluster_error
    def find(self, name: str) -> Servable:
        """
        Search for a Servable with a given name.

        :param name: a name of the servable
        :return: a Servable instance
        """
        return Servable.find_by_name(self.cluster, name)

    @handle_cluster_error
    def logs(self, name: str, follow: bool = False):
        return self.find(name).logs(follow)
