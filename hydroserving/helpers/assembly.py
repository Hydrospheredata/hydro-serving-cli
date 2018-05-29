import os
import tarfile

import click

from hydroserving.constants.package import TARGET_PATH, PACKAGE_FILES_PATH
from hydroserving.helpers.package import pack_model


def assemble_model(model):
    files = pack_model(model)
    package_name = "{}.tar.gz".format(model.name)
    package_path = os.path.join(TARGET_PATH, package_name)
    with click.progressbar(iterable=files,
                           item_show_func=lambda x: x,
                           label='Assembling the model') as bar:

        with tarfile.open(package_path, "w:gz") as tar:
            tar_name = tar.name
            for entry in bar:
                relative_name = os.path.relpath(entry, PACKAGE_FILES_PATH)
                tar.add(entry, arcname=relative_name)

    return tar_name
