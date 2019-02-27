"""
Filesystem utilities
"""

import os
import shutil
import glob


def resolve_list_of_globs(globs):
    """
    Iterates over payload paths and recursively retrieves visible files

    Args:
        globs (list of str):

    Returns:
        dict: key - parent path of file, value - files within parent component

    """
    paths = []
    for glob_path in globs:
        expanded = os.path.expanduser(glob_path)
        unglobbed = glob.glob(expanded)
        for path in unglobbed:
            if os.path.exists(path):
                paths.append(path)
            else:
                raise ValueError("Path {} doesn't exist".format(path))
    return paths


def copy_to_target(src_path, package_path):
    """
    Copies file or directory from src_path to package_path,
    while resolving relative names.

    Args:
        src_path (str):
        package_path (str):
    """
    basename = os.path.basename(src_path)

    packed_path = os.path.join(package_path, basename)
    if os.path.isfile(src_path):
        shutil.copy(src_path, packed_path)
    elif os.path.isdir(src_path):
        shutil.copytree(src_path, packed_path)
    else:
        raise FileNotFoundError(src_path)
    return packed_path


def with_cwd(new_cwd, func, *args):
    """
    Wrapper util to run some function in new Current Working Directory
    :param new_cwd: path to the new CWD
    :param func: callback
    :param args: args to the `func`
    :return: result of `func`
    """
    old_cwd = os.getcwd()
    try:
        os.chdir(new_cwd)
        result = func(*args)
        return result
    except Exception as err:
        raise err
    finally:
        os.chdir(old_cwd)


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
    return [
        os.path.join(path, file)
        for file in os.listdir(path)
        if not file.startswith('.')
    ]


def is_yaml(path):
    """
    Checks if file's extension is .yaml or .yml
    Args:
        path:

    Returns:

    """
    ext = os.path.splitext(path)[1]
    return os.path.isfile(path) and (ext in (".yml", ".yaml"))


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


def read_in_chunks(file_object, chunk_size=1024):
    """Lazy function (generator) to read a file piece by piece.
    Default chunk size: 1k."""
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data
