import os
import shutil

import click

from hydroserving.constants.package import PACKAGE_FILES_PATH, PACKAGE_CONTRACT_PATH, TARGET_PATH
from hydroserving.helpers.contract import read_contract_cwd


def pack_path(entry):
    model_dirs = os.path.dirname(entry)
    packed_dirs = os.path.join(PACKAGE_FILES_PATH, model_dirs)
    if not os.path.exists(packed_dirs):
        os.makedirs(packed_dirs)

    if os.path.isdir(entry):
        for sub_entry in os.listdir(entry):
            pack_path(os.path.join(entry, sub_entry))
    else:
        click.echo("Copy: {}".format(entry))
        packed_path = os.path.join(PACKAGE_FILES_PATH, entry)
        shutil.copy(entry, packed_path)


def pack_payload(model):
    if not os.path.exists(PACKAGE_FILES_PATH):
        os.makedirs(PACKAGE_FILES_PATH)
    for entry in model.payload:
        pack_path(entry)
    return PACKAGE_FILES_PATH


def pack_contract(model):
    contract = read_contract_cwd(model)
    contract_destination = os.path.join(PACKAGE_CONTRACT_PATH)

    with open(contract_destination, "wb") as contract_file:
        contract_file.write(contract.SerializeToString())

    return contract_destination


def pack_model(model):
    click.echo("Packing model snapshot...")
    payload_path = pack_payload(model)
    contract_path = pack_contract(model)
    return [payload_path, contract_path]


def execute_build_steps(build_steps):
    idx = 1
    for build_step in build_steps:
        click.echo("[{}] {}".format(idx, build_step))
        os.system(build_step)
        idx += 1


def with_cwd(new_cwd, func, *args):
    old_cwd = os.getcwd()
    os.chdir(new_cwd)
    func(args)
    os.chdir(old_cwd)


def build_model(metadata):
    build_steps = metadata.local_deployment.build

    if build_steps is None or not build_steps:
        click.echo("No build steps. Skipping...")
        return None

    click.echo("Build steps detected. Executing...")
    with_cwd(TARGET_PATH, execute_build_steps, build_steps)
    click.echo("Done.")
