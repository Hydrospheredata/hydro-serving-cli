import os

from hs.util.fileutil import get_visible_files, get_yamls

MODEL_FOLDER = "./examples/local_dev"


def test_get_all_visible_files():
    hidden_path = os.path.join(MODEL_FOLDER, ".ninja.file")
    print(hidden_path)
    with open(hidden_path, "w"):
        files = get_visible_files(MODEL_FOLDER)
        print(files)
        assert hidden_path not in files
        assert os.path.join(MODEL_FOLDER, "serving.yaml") in files
        assert os.path.join(MODEL_FOLDER, "calculator") in files
    os.remove(hidden_path)


def test_get_all_visible_files_recursively():
    hidden_path = os.path.join(MODEL_FOLDER, ".ninja.file")
    print(hidden_path)
    with open(hidden_path, "w"):
        files = get_visible_files(MODEL_FOLDER, recursive=True)
        print(files)
        assert hidden_path not in files
        assert os.path.join(MODEL_FOLDER, "calculator/src/func_main.py") in files
        assert os.path.join(MODEL_FOLDER, "calculator/requirements.txt") in files
    os.remove(hidden_path)


def test_get_all_yaml_files():
    files = get_yamls(MODEL_FOLDER)
    print(files)
    assert [os.path.join(MODEL_FOLDER, "serving.yaml")] == files