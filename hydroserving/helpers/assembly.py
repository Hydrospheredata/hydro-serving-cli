import os
import tarfile

import click

from hydroserving.constants.package import PACKAGE_FILES_PATH
from hydroserving.helpers.package import pack_model


def assemble_model(model):
    pack_model(model)
    package_name = "{}.tar.gz".format(model.name)
    package_path = os.path.join("target", package_name)
    click.echo("Assembling {} ...".format(package_path))
    model_root = os.path.join("target", "model")
    files_root = os.path.join(model_root, "files")
    with tarfile.open(package_path, "w:gz") as tar:
        tar_name = tar.name
        relative_name = os.path.relpath(PACKAGE_FILES_PATH, files_root)
        tar.add(PACKAGE_FILES_PATH, arcname=relative_name)
    return tar_name
