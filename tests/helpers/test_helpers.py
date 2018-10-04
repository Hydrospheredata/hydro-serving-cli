import os

from hydroserving.helpers.file import get_visible_files, get_yamls

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

# def test_assembly_with_metadata():
#     def _test_assembly_with_metadata():
#         folder_metadata = FolderMetadata.from_directory(".")
#         print(folder_metadata)
#         result = assemble_model(folder_metadata.model)
#
#         print(result)
#         assert os.path.exists(os.path.join(".", TARGET_PATH, "example_script.tar.gz"))
#         assert os.listdir(os.path.join(".", PACKAGE_FILES_PATH))
#
#     with_target_cwd(MODEL_FOLDER, _test_assembly_with_metadata)
#
#
# def test_assemble_without_metadata():
#     path = os.path.join(MODEL_FOLDER, "calculator")
#
#     def _test_assemble_without_metadata():
#         model = ModelDefinition(
#             "model",
#             "test:test",
#             None,
#             ['.'],
#             "Description"
#         )
#         result = assemble_model(model)
#         print(result)
#         assert os.path.exists(os.path.join(".", TARGET_PATH, "model.tar.gz"))
#         assert os.listdir(os.path.join(".", PACKAGE_FILES_PATH))
#
#     with_target_cwd(path, _test_assemble_without_metadata)
