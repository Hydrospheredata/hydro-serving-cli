import unittest
import os
import shutil

from hydroserving.cli import ensure_model
from hydroserving.helpers.package import assemble_model

MODEL_FOLDER = "./tests/test_metadata_resources/"
TRASH_FOLDER = "./tests/.hs"


def pack_model(model_name):
    path = os.path.abspath(os.path.join(MODEL_FOLDER, model_name))

    model = ensure_model(path, model_name, "type", "desc", None, None)
    result = assemble_model(model, TRASH_FOLDER)
    return result


class PackagingTests(unittest.TestCase):
    def test_upload_no_metadata(self):
        modelname = "no_metadata"
        pack_model(modelname)
        files_path = os.path.join(TRASH_FOLDER, modelname, "files")
        files = os.listdir(files_path)
        assert 'data_folder' in files
        assert 'file1.txt' in files
        data_path = os.path.join(files_path, 'data_folder')
        data_files = os.listdir(data_path)
        assert 'file2.txt' in data_files
        assert 'subfolder' in data_files

    def test_upload_with_metadata(self):
        modelname = "upload"
        pack_model(modelname)
        files_path = os.path.join(TRASH_FOLDER, modelname, "files")
        files = os.listdir(files_path)
        assert 'file1.txt' in files
        assert 'data_folder' in files
        data_path = os.path.join(files_path, 'data_folder')
        data_files = os.listdir(data_path)
        assert 'file2.txt' in data_files
        assert 'subfolder' in data_files

    def test_apply_model(self):
        modelname = "apply"
        pack_model(modelname)
        files_path = os.path.join(TRASH_FOLDER, modelname, "files")
        files = os.listdir(files_path)
        assert 'data_folder' in files
        data_path = os.path.join(files_path, 'data_folder')
        data_files = os.listdir(data_path)
        assert 'file2.txt' in data_files
        assert 'subfolder' in data_files

    def tearDown(self):
        shutil.rmtree(TRASH_FOLDER)
