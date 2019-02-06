from abc import ABC, abstractmethod
import yaml


class ParserError(RuntimeError):
    def __init__(self, file, msg):
        super().__init__(msg)
        self.file = file


class UnknownResource(ParserError):
    def __init__(self, file, kind):
        super().__init__(file, "Can't find a parser for resource {}".format(kind))


class AbstractParser(ABC):
    def yaml_file_stream(self, file):
        try:
            yaml_dict_stream = yaml.safe_load_all(file)
            for yaml_dict in yaml_dict_stream:
                yield self.parse_dict(yaml_dict)
        except ParserError as ex:
            raise ParserError(file, ex)
        except KeyError as ex:
            raise ParserError(file, "Can't find {} field".format(ex))

    def yaml_file(self, file):
        try:
            yaml_dict = yaml.safe_load(file)
            return self.parse_dict(yaml_dict)
        except ParserError as ex:
            raise ParserError(file, ex)
        except KeyError as ex:
            raise ParserError(file, "Can't find {} field".format(ex))

    def write_yaml(self, yaml_path, obj):
        """
        Writes object to yaml file

        Args:
            yaml_path (str): path to yaml file
            obj (object): object to dump

        Returns:
            Nothing

        """
        yaml_dict = self.to_dict(obj)
        with open(yaml_path, 'w') as f:
            yaml.safe_dump(yaml_dict, f)

    @abstractmethod
    def parse_dict(self, in_dict):
        """
        Parses dict with model definition and creates a model

        Args:
            in_dict (dict):

        Returns:
            object: if parse is successful
        """
        pass

    @abstractmethod
    def to_dict(self, obj):
        """
        Converts object to dict with neccessary metadata

        Args:
            obj (object): object to convert

        Returns:
            dict: if conversion is successful

        """
        pass
