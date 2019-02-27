import yaml
from yaml.parser import ParserError


def yaml_file_stream(file):
    try:
        res = []
        for yaml_dict in yaml.safe_load_all(file):
            res.append(yaml_dict)
        return res
    except ParserError as ex:
        raise ParserError(file, ex)
    except KeyError as ex:
        raise ParserError(file, "Can't find {} field".format(ex))


def yaml_file(file):
    try:
        yaml_dict = yaml.safe_load(file)
        return yaml_dict
    except ParserError as ex:
        raise ParserError(file, ex)
    except KeyError as ex:
        raise ParserError(file, "Can't find {} field".format(ex))


def write_yaml(yaml_path, data_dict):
    """
    Writes object to yaml file

    Args:
        data_dict:
        yaml_path (str): path to yaml file

    Returns:
        Nothing

    """
    with open(yaml_path, 'w') as f:
        yaml.safe_dump(data_dict, f)
