import os
from urllib.parse import urlsplit, urlunsplit
from typing import List, Optional
import click

from hydroserving.config.cluster_config import ClusterConfig
from hydroserving.config.parser import parse_config
from hydroserving.config.settings import CONFIG_FILE
from hydroserving.util.yamlutil import yaml_file, write_yaml
from hydroserving.errors.config import (
    ParseConfigurationError, ClusterNotFoundError, ClusterAlreadyExistsError,
)

CLUSTER_COMPONENTS_INFO = [
    "/api/buildinfo",
    "/gateway/buildinfo",
    "/monitoring/buildinfo"
]


class ConfigService:
    """
    Entry point for CLI configuration.

    Works with configuration yaml files under `home_path` directory
    """
    def __init__(self, home_path: str = '~/.hs-home', overridden_cluster: str = None):
        self.home_path          = home_path
        self.config_path        = os.path.join(home_path, CONFIG_FILE)
        self.overridden_cluster = overridden_cluster
        
        if not os.path.exists(home_path):
            click.echo(f"{home_path} is not an existing directory, creating one")
            os.makedirs(home_path)
        
        if not os.path.exists(self.config_path):
            click.echo(f"{self.config_path} is not an existing configuration file, creating a new one")
            self.config = ClusterConfig()
            write_yaml(self.config_path, self.config.__dict__)
        else:
            try:
                if os.path.isfile(self.config_path):
                    with open(self.config_path, 'r') as f:
                        doc = yaml_file(f)
                        self.config = parse_config(doc)
                else:
                    raise ValueError(f"{self.config_path} is not a file")
            except Exception as e:
                raise ParseConfigurationError(f"Could not parse the configuration file {self.config_path}") from e

    def select_cluster(self, cluster_name: str) -> dict:
        cluster = self.find_cluster(cluster_name)
        self.config.current_cluster = cluster['name']
        write_yaml(self.config_path, self.config.__dict__)
        return cluster

    def list_clusters(self) -> List[dict]:
        return self.config.clusters

    def add_cluster(self, name: str, endpoint: str) -> dict:
        url = urlsplit(endpoint)
        if not url.scheme or not url.netloc:
            raise ValueError(f"Invalid cluster address '{endpoint}'")

        try:
            cluster = self.find_cluster(name)
            raise ClusterAlreadyExistsError()
        except ClusterNotFoundError:
            pass
        
        cluster = dict(
            cluster=dict(server=urlunsplit([url.scheme, url.netloc, "", "", ""])),
            name=name,
        )
        self.config.clusters.append(cluster)
        if not self.config.current_cluster:
            click.echo(f"Using {name} as current cluster")
            self.config.current_cluster = name
        write_yaml(self.config_path, self.config.__dict__)
        return cluster

    def remove_cluster(self, name: str) -> Optional[dict]:
        try:
            cluster = self.find_cluster(name)
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
        except ClusterNotFoundError:
            click.echo(f"Cluster {name} not found")

    def find_cluster(self, cluster_name: str) -> dict:
        for c in self.config.clusters:
            if c['name'] == cluster_name:
                return c
        raise ClusterNotFoundError(cluster_name)

    def current_cluster(self) -> dict:
        if self.overridden_cluster:
            return self.find_cluster(self.overridden_cluster)
        return self.find_cluster(self.config.current_cluster)
