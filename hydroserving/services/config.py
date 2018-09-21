import os
import logging

from hydroserving.constants.config import CONFIG_FILE
from hydroserving.models.definitions.config import Config
from hydroserving.parsers.config import ConfigParser


class ConfigService:
    def __init__(self, home_path):
        self.home_path = home_path
        self.config_path = os.path.join(home_path, CONFIG_FILE)
        self.confparser = ConfigParser()
        if os.path.isfile(self.config_path):
            self.config = self.confparser.parse_yaml(self.config_path)
        else:
            logging.error("{} is not an existing directory", home_path)
            self.config = Config()
            self.confparser.write_yaml(self.config_path, self.config)

    def select_cluster(self, cluster_name):
        cluster = self.find_cluster(cluster_name)
        if cluster is not None:
            self.config.current_cluster = cluster['name']
            self.confparser.write_yaml(self.config_path, self.config)
            return cluster
        else:
            return None

    def list_clusters(self):
        return list(self.config.clusters)

    def add_cluster(self, name, endpoint):
        cluster = self.find_cluster(name)
        if cluster is None:
            cluster = {
                'cluster': {
                    'server': endpoint
                },
                'name': name
            }
            self.config.clusters.append(cluster)
            if self.config.current_cluster is None:
                logging.warning("Using {} as current cluster".format(name))
                self.config.current_cluster = name
            self.confparser.write_yaml(self.config_path, self.config)
            return cluster
        else:
            return None

    def remove_cluster(self, name):
        cluster = self.find_cluster(name)
        if cluster is not None:
            self.config.clusters.remove(cluster)
            if cluster['name'] == self.config.current_cluster:
                logging.warning("Current cluster is deleted")
                if len(self.config.clusters) == 0:
                    self.config.current_cluster = None
                else:
                    self.config.current_cluster = self.config.clusters[0]['name']
                logging.warning("New current cluster: {}".format(self.config.current_cluster))

        self.confparser.write_yaml(self.config_path, self.config)
        return cluster

    def find_cluster(self, cluster_name):
        for c in self.config.clusters:
            if c['name'] == cluster_name:
                return c
        return None

    def current_cluster(self):
        return self.find_cluster(self.config.current_cluster)
