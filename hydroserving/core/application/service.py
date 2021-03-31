import logging
import time
from typing import List, Callable

from hydroserving.core.application.entities import model_variant
from hydroserving.util.err_handler import handle_cluster_error
from hydrosdk.cluster import Cluster
from hydrosdk.application import Application, ApplicationBuilder
from hydrosdk.exceptions import BadRequestException


class ApplicationService:
    def __init__(self, cluster: Cluster):
        self.cluster = cluster

    @handle_cluster_error
    def apply(self, partial_parser: Callable[[Cluster], Application]) -> Application:
        """
        Create a Application on the cluster.
        
        :param partial_parser: a partial function, which will create an application
        :return: Application instance
        """
        return partial_parser(self.cluster)

    @handle_cluster_error
    def list(self) -> List[Application]:
        """
        List all available applications on the cluster.

        :return: list of Application instances
        """
        return Application.list(self.cluster)

    @handle_cluster_error
    def find(self, name: str) -> Application:
        """
        Find an application by name. 

        :param name: application name
        :return: Application instance
        """
        return Application.find(self.cluster, name)

    @handle_cluster_error
    def delete(self, name: str) -> dict:
        """
        Delete an application by name.

        :param name: application name
        :return: json response from the cluster
        """
        return Application.delete(self.cluster, name)
