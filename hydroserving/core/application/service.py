import logging
import time
from typing import List

from hydroserving.core.application.entities import model_variant
from hydrosdk.cluster import Cluster
from hydrosdk.application import Application, ApplicationBuilder
from hydrosdk.exceptions import BadRequestException


class ApplicationService:
    def __init__(self, cluster: Cluster):
        self.cluster = cluster

    def apply(self, builder: ApplicationBuilder, timeout: int = 120) -> Application:
        """
        Create or update an Application on the cluster.

        :param builder: an instance of the ApplicationBuilder with all required attributes
        :param timeout: timeout for waiting for the application to start
        :return: Application instance
        """
        logging.debug("Applying application: %s", builder.name)

        try:
            _ = self.find(builder.name)
            logging.warning("Found an existing application, update required")
        except BadRequestException:
            logging.debug("Creating application: %s", builder)
            application = builder.build()
        application.lock_while_starting(timeout)

    def list(self) -> List[Application]:
        """
        List all available applications on the cluster.

        :return: list of Application instances
        """
        return Application.list(self.cluster)

    def find(self, name: str) -> Application:
        """
        Find an application by name. 

        :param name: application name
        :return: Application instance
        """
        return Application.find(self.cluster, name)

    def delete(self, name: str) -> dict:
        """
        Delete an application by name.

        :param name: application name
        :return: json response from the cluster
        """
        return Application.delete(self.cluster, name)
