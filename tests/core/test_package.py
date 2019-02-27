import unittest
import os
import shutil
import tarfile

from hydroserving.core.model.package import assemble_model, ensure_model

MODEL_FOLDER = "./tests/test_metadata_resources/"
TRASH_FOLDER = "./tests/.hs"


def pack_model(model_name):
    path = os.path.abspath(os.path.join(MODEL_FOLDER, model_name))

    model = ensure_model(path, model_name, "type", "desc", None)
    result = assemble_model(model, TRASH_FOLDER)
    return result


class PackagingTests(unittest.TestCase):
    def test_upload_no_metadata(self):
        modelname = "no_metadata"
        tar = pack_model(modelname)
        with tarfile.open(tar, "r:gz") as file:
            names = file.getnames()
            print(names)
            assert "file1.txt" in names
            assert 'data_folder/file2.txt' in names
            assert 'data_folder/subfolder/file3.txt' in names

    def test_upload_with_metadata(self):
        modelname = "upload"
        tar = pack_model(modelname)
        with tarfile.open(tar, "r:gz") as file:
            names = file.getnames()
            print(names)
            assert "file1.txt" in names
            assert 'data_folder/file2.txt' in names
            assert 'data_folder/subfolder/file3.txt' in names

    def test_apply_model(self):
        modelname = "apply"
        tar = pack_model(modelname)
        with tarfile.open(tar, "r:gz") as file:
            names = file.getnames()
            print(names)
            assert "file2.txt" in names
            assert 'subfolder/file3.txt' in names

    def tearDown(self):
        shutil.rmtree(TRASH_FOLDER)
