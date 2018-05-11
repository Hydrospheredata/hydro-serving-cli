import os
import shutil

import click

from hydroserving.constants.package import PACKAGE_FILES_PATH, PACKAGE_CONTRACT_PATH, TARGET_PATH
from hydroserving.helpers.contract import read_contract_cwd


def get_subfiles(path):
    return [os.path.join(dir_name, file) for dir_name, _, files in os.walk(path) for file in files]


def get_payload_files(payload):
    files = []
    for x in payload:
        if os.path.isfile(x):
            files.append(x)
        else:
            sub_files = get_subfiles(x)
            for sub_file in sub_files:
                files.append(sub_file)
    return files


def copy_to_target(src_path):
    model_dirs = os.path.dirname(src_path)
    packed_dirs = os.path.join(PACKAGE_FILES_PATH, model_dirs)
    if not os.path.exists(packed_dirs):
        os.makedirs(packed_dirs)
    packed_path = os.path.join(PACKAGE_FILES_PATH, src_path)
    shutil.copy(src_path, packed_path)
    return packed_path


def pack_payload(model):
    if not os.path.exists(PACKAGE_FILES_PATH):
        os.makedirs(PACKAGE_FILES_PATH)

    files = get_payload_files(model.payload)

    copied_files = []
    with click.progressbar(iterable=files,
                           item_show_func=lambda x: x,
                           label='Packing the model') as bar:
        for entry in bar:
            copied_file = copy_to_target(entry)
            copied_files.append(copied_file)

    return copied_files


def pack_contract(model):
    contract = read_contract_cwd(model)
    contract_destination = os.path.join(PACKAGE_CONTRACT_PATH)

    with open(contract_destination, "wb") as contract_file:
        contract_file.write(contract.SerializeToString())

    return contract_destination


def pack_model(model):
    payload_files = pack_payload(model)
    if model.contract_path is not None:
        pack_contract(model)
    return payload_files


def execute_build_steps(build_steps):
    idx = 1
    for build_step in build_steps:
        click.echo("[{}] {}".format(idx, build_step))
        os.system(build_step)
        idx += 1


def with_cwd(new_cwd, func, *args):
    old_cwd = os.getcwd()
    os.chdir(new_cwd)
    result = func(*args)
    os.chdir(old_cwd)
    return result


def build_model(metadata):
    build_steps = metadata.local_deployment.build

    if build_steps is None or not build_steps:
        click.echo("No build steps. Skipping...")
        return None

    click.echo("Build steps detected. Executing...")
    with_cwd(TARGET_PATH, execute_build_steps, build_steps)
    click.echo("Done.")
