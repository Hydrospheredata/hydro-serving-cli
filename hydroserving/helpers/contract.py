import os

import hydro_serving_grpc as hs
from google.protobuf import text_format


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
