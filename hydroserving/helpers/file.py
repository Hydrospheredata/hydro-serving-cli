import os


def get_visible_files(path, recursive=False):
    """
    Recursively lists visible files
    :param recursive: recursive search?
    :param path: Path to look for
    :return: flat list of visible files
    """
    if recursive:
        return [
            os.path.join(dir_name, file)
            for dir_name, _, files in os.walk(path)
            for file in files
            if not file.startswith('.')
        ]
    else:
        return [
            os.path.join(path, file)
            for file in os.listdir(path)
            if not file.startswith('.')
        ]


def is_yaml(path):
    ext = os.path.splitext(path)[1]
    return os.path.isfile(path) and (ext == ".yml" or ext == ".yaml")


def get_yamls(path):
    """
    Returns all yaml files.

    Searches for files with ``.yml`` or ``.yaml`` extensions.

    :param path: where to search
    :return: list of paths to yaml files
    """

    return [
        file
        for file in get_visible_files(path)
        if is_yaml(file)
    ]
