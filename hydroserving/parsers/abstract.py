from abc import ABC, abstractmethod
import yaml


class AbstractParser(ABC):
    def parse_yaml_stream(self, yaml_path):
        """
        Reads stream of documents from file.
        Assumes that every doc in stream is the same kind.
        :param yaml_path: a path to yaml
        :return: a stream of models
        """
        with open(yaml_path, 'r') as f:
            yaml_dict_stream = yaml.safe_load_all(f)

        for yaml_dict in yaml_dict_stream:
            yield self.parse_dict(yaml_dict)

    def parse_yaml(self, yaml_path):
        """
        Reads single doc from file.
        :param yaml_path: a path to yaml
        :return: a model
        """
        with open(yaml_path, 'r') as f:
            yaml_dict = yaml.safe_load(f)
        return self.parse_dict(yaml_dict)

    @abstractmethod
    def parse_dict(self, in_dict):
        """
        Parses dict with model definition and creates a model
        :param in_dict: a dict with definition
        :return: a model
        """
        pass
