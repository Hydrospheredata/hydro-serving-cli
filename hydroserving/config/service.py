import logging
import os
from json import JSONDecodeError
from urllib.parse import urlsplit, urlunsplit, urljoin
from typing import List, Optional

import click
from click import Abort
import requests
from requests import ConnectionError, ConnectTimeout
from hydrosdk.cluster import Cluster
from hydroserving.config.cluster_config import ClusterConfig
from hydroserving.config.parser import parse_config
from hydroserving.config.settings import CONFIG_FILE
from hydroserving.util.yamlutil import yaml_file, write_yaml
from hydroserving.errors.config import (
    ParseConfigurationError, ClusterNotFoundError, ClusterAlreadyExistsError,
)


class ConfigService:
    """
    Entrypoint for CLI configuration.

    Works with configuration yaml files under `home_path` directory
    """
    def __init__(self, home_path: str = '~/.hs-home', overridden_cluster: str = None):
        self.home_path          = home_path
        self.config_path        = os.path.join(home_path, CONFIG_FILE)
        self.overridden_cluster = overridden_cluster
        
        if not os.path.exists(home_path):
            logging.debug(f"{home_path} is not an existing directory, creating one")
            os.makedirs(home_path)
        if not os.path.exists(self.config_path):
            logging.debug(f"{self.config_path} is not an existing configuration file, creating a new one")
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

    def select_cluster(self, name: str) -> dict:
        cluster = self.find_cluster(name)
        self.config.current_cluster = cluster['name']
        write_yaml(self.config_path, self.config.__dict__)
        return cluster

    def list_clusters(self) -> List[dict]:
        return self.config.clusters

    def add_cluster(self, name: str, endpoint: str) -> dict:
        # Validate name and endpoint
        url = urlsplit(endpoint)
        if not url.scheme or not url.netloc:
            raise ValueError(f"Invalid cluster address '{endpoint}'")
        try:
            cluster = self.find_cluster(name)            
            raise ClusterAlreadyExistsError()
        except ClusterNotFoundError:
            pass
            
        # Check, if provided endpoint is already registered
        server = urlunsplit([url.scheme, url.netloc, "", "", ""])
        existing = list(filter(
            lambda x: x.get('cluster', {}).get('server', 'unknown') == server, 
            self.config.clusters
        ))
        if existing: 
            logging.warning(f"There's already an existing cluster '{existing[0].get('name', 'unknown')}' with equal server endpoint.")
            proceed = click.prompt("Do you want to add another one? [Y/n]", type=bool)
            if not proceed:
                raise Abort()

        # Add new cluster entity
        cluster = {"name": name, "cluster": {"server": server}}
        self.config.clusters.append(cluster)
        if not self.config.current_cluster:
            logging.info(f"Using '{name}' as current cluster")
            self.config.current_cluster = name
        write_yaml(self.config_path, self.config.__dict__)
        return cluster

    def remove_cluster(self, name: str) -> dict:
        cluster = self.find_cluster(name)
        self.config.clusters.remove(cluster)
        if cluster['name'] == self.config.current_cluster:
            logging.info("Current cluster is deleted")
            if len(self.config.clusters) == 0:
                self.config.current_cluster = None
            else:
                self.config.current_cluster = self.config.clusters[0]['name']
                logging.info("New current cluster: {}".format(self.config.current_cluster))
        write_yaml(self.config_path, self.config.__dict__)
        return cluster
        
    def find_cluster(self, cluster_name: str) -> dict:
        for c in self.config.clusters:
            if c['name'] == cluster_name:
                return c
        raise ClusterNotFoundError(cluster_name)

    def current_cluster(self) -> dict:
        if self.overridden_cluster:
            return self.find_cluster(self.overridden_cluster)
        return self.find_cluster(self.config.current_cluster)

    def get_cluster_buildinfo(self) -> list:
        try:
            return Cluster(self.current_cluster()["cluster"]["server"]).build_info()
        except KeyError as e:
            logging.error(f"Couldn't read malformed cluster definition: {self.current_cluster()}")
