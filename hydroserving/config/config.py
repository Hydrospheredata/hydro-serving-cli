import os
import click
from urllib.parse import urlparse, urlunparse, urlsplit, urlunsplit

from hydroserving.config.cluster_config import ClusterConfig
from hydroserving.config.settings import CONFIG_FILE
from hydroserving.core.parsers.config import ConfigParser
from hydroserving.http.remote_connection import RemoteConnection


class ConfigService:
    """
    Entry point for CLI configuration.

    Works with configuration yaml files under `home_path` directory
    """

    def __init__(self, home_path):
        self.home_path = home_path
        self.config_path = os.path.join(home_path, CONFIG_FILE)
        self.confparser = ConfigParser()
        if os.path.isfile(self.config_path):
            self.config = self.confparser.parse_yaml(self.config_path)
        else:
            click.echo("{} is not an existing directory".format(home_path))
            self.config = ClusterConfig()
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
        url = urlsplit(endpoint)
        if not url.scheme or not url.netloc:
            raise ValueError("Invalid cluster address '{}'".format(endpoint))
        cluster = self.find_cluster(name)
        if cluster is None:
            cluster = {
                'cluster': {
                    'server': urlunsplit([url.scheme, url.netloc, "", "", ""])
                },
                'name': name
            }
            self.config.clusters.append(cluster)
            if self.config.current_cluster is None:
                click.echo("Using {} as current cluster".format(name))
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
                click.echo("Current cluster is deleted")
                if len(self.config.clusters) == 0:
                    self.config.current_cluster = None
                else:
                    self.config.current_cluster = self.config.clusters[0]['name']
                click.echo("New current cluster: {}".format(self.config.current_cluster))

        self.confparser.write_yaml(self.config_path, self.config)
        return cluster

    def find_cluster(self, cluster_name):
        for c in self.config.clusters:
            if c['name'] == cluster_name:
                return c
        return None

    def current_cluster(self):
        return self.find_cluster(self.config.current_cluster)

    def get_connection(self):
        current_cluster = self.current_cluster()
        if current_cluster is not None:
            return RemoteConnection(current_cluster['cluster']['server'])
        else:
            return None
