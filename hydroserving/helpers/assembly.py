import os
import tarfile

import click

from hydroserving.constants.package import PACKAGE_FILES_PATH
from hydroserving.helpers.package import pack_model


def assemble_model(model):
    files = pack_model(model)
    package_name = "{}.tar.gz".format(model.name)
    package_path = os.path.join("target", package_name)
    model_root = os.path.join("target", "model")
    files_root = os.path.join(model_root, "files")
    with click.progressbar(iterable=files,
                           item_show_func=lambda x: x,
                           label='Assembling the model') as bar:

        with tarfile.open(package_path, "w:gz") as tar:
            tar_name = tar.name
            for entry in bar:
                relative_name = os.path.relpath(entry, files_root)
                tar.add(entry, arcname=relative_name)

    return tar_name
