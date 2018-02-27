import click
import tarfile
import os
import shutil
import hydro_serving_grpc as hs
from google.protobuf import text_format

from hydroserving.constants import PACKAGE_FILES_PATH, PACKAGE_CONTRACT_PATH


def read_contract(model):
    _, file_ext = os.path.splitext(model.contract_path)
    contract = hs.ModelContract()

    if file_ext == ".protobin":
        with open(model.contract_path, "rb") as contract_file:
            contract.ParseFromString(contract_file.read())
    elif file_ext == ".prototxt":
        with open(model.contract_path, "r") as contract_file:
            text_format.Parse(contract_file.read(), contract)
    else:
        raise RuntimeError("Unsupported contract extension")
    return contract


def pack_contract(model):
    contract = read_contract(model)
    contract_destination = os.path.join(PACKAGE_CONTRACT_PATH)

    with open(contract_destination, "wb") as contract_file:
        contract_file.write(contract.SerializeToString())

    return contract_destination


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


def pack_model(model):
    payload_path = pack_payload(model)
    contract_path = pack_contract(model)
    return [payload_path, contract_path]


def assemble_model(model, payload_list):
    package_name = "{}.tar.gz".format(model.name)
    package_path = os.path.join("target", package_name)
    with tarfile.open(package_path, "w:gz") as tar:
        tar_name = tar.name
        for entry in payload_list:
            tar.add(entry)
    return tar_name
