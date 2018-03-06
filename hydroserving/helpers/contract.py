import os

import hydro_serving_grpc as hs
from google.protobuf import text_format


def read_contract_cwd(model):
    return read_contract_file(model.contract_path)


def read_contract_file(contract_path):
    _, file_ext = os.path.splitext(contract_path)
    contract = hs.ModelContract()

    if file_ext == ".protobin":
        with open(contract_path, "rb") as contract_file:
            contract.ParseFromString(contract_file.read())
    elif file_ext == ".prototxt":
        with open(contract_path, "r") as contract_file:
            text_format.Parse(contract_file.read(), contract)
    else:
        raise RuntimeError("Unsupported contract extension")
    return contract
