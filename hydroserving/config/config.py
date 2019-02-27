import os
from urllib.parse import urlsplit, urlunsplit

import click

from hydroserving.config.cluster_config import ClusterConfig
from hydroserving.config.parser import parse_config
from hydroserving.config.settings import CONFIG_FILE
from hydroserving.http.remote_connection import RemoteConnection
from hydroserving.util.yamlutil import yaml_file, write_yaml


class ConfigService:
    """
    Entry point for CLI configuration.

    Works with configuration yaml files under `home_path` directory
    """

    def __init__(self, home_path, overridden_cluster=None):
        self.home_path = home_path
        self.config_path = os.path.join(home_path, CONFIG_FILE)
        self.overriden_cluster = overridden_cluster
        if os.path.isfile(self.config_path):
            with open(self.config_path, 'r') as f:
                doc = yaml_file(f)
                self.config = parse_config(doc)
        else:
            click.echo("{} is not an existing directory".format(home_path))
            self.config = ClusterConfig()
            write_yaml(self.config_path, self.config.__dict__)

    def select_cluster(self, cluster_name):
        cluster = self.find_cluster(cluster_name)
        if cluster:
            self.config.current_cluster = cluster['name']
            write_yaml(self.config_path, self.config.__dict__)
            return cluster
        return None

    def list_clusters(self):
        return list(self.config.clusters)

    def add_cluster(self, name, endpoint):
        url = urlsplit(endpoint)
        if not url.scheme or not url.netloc:
            raise ValueError("Invalid cluster address '{}'".format(endpoint))
        cluster = self.find_cluster(name)
        if cluster:
            return None
        cluster = {
            'cluster': {
                'server': urlunsplit([url.scheme, url.netloc, "", "", ""])
            },
            'name': name
        }
        self.config.clusters.append(cluster)
        if not self.config.current_cluster:
            click.echo("Using {} as current cluster".format(name))
            self.config.current_cluster = name
        write_yaml(self.config_path, self.config.__dict__)
        return cluster

    def remove_cluster(self, name):
        cluster = self.find_cluster(name)
        if cluster:
            self.config.clusters.remove(cluster)
            if cluster['name'] == self.config.current_cluster:
                click.echo("Current cluster is deleted")
                if len(self.config.clusters) == 0:
                    self.config.current_cluster = None
                else:
                    self.config.current_cluster = self.config.clusters[0]['name']
                click.echo("New current cluster: {}".format(self.config.current_cluster))

        write_yaml(self.config_path, self.config.__dict__)
        return cluster

    def find_cluster(self, cluster_name):
        for c in self.config.clusters:
            if c['name'] == cluster_name:
                return c
        return None

    def current_cluster(self):
        if self.overriden_cluster:
            return self.find_cluster(self.overriden_cluster)
        return self.find_cluster(self.config.current_cluster)

    def get_connection(self):
        current_cluster = self.current_cluster()
        if current_cluster:
            return RemoteConnection(current_cluster['cluster']['server'])
        return None

    def get_cluster_connection(self, cluster_name):
        current_cluster = self.find_cluster(cluster_name)
        if current_cluster:
            return RemoteConnection(current_cluster['cluster']['server'])
        return None
