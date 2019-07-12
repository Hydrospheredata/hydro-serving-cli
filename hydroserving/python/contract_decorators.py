import ast
import pathlib
import sys
from functools import wraps
import os
import inspect
import grpc
import hydro_serving_grpc as hsg
import hydro_serving_grpc.contract as hsc
import hydroserving.core.contract as ctr
from hydroserving.python.server import PythonRuntime

# PYTHON MODEL DECORATORS

class ContractError(Exception):
    pass

def create_client(channel):
    stub = hsg.PredictionServiceStub(channel)
    return stub.Predict

def entrypoint(on_init=None):
    """
    Args:
        on_init: callback with no arguments and ignored return
            will be called during model initialization
    """
    def _entrypoint(func):
        inputs = []
        for k, v in func._serving_inputs.items():
            inputs.append(ctr.field_from_dict(k, v.to_definition()))
        outputs = []
        for k, v in func._serving_outputs.items():
            outputs.append(ctr.field_from_dict(k, v.to_definition()))
        
        func._serving_signature = ctr.ModelSignature(
                signature_name = func.__name__,
                inputs = inputs,
                outputs = outputs
            )
        func._serving_contract = ctr.ModelContract(
            model_name = func.__name__,
            predict = func._serving_signature
        )

        func._serving_init = on_init

        func._serving_server = PythonRuntime(func)
        func._serving_client = create_client
        return func
    return _entrypoint

def inputs(**fields):
    def dec(func):
        func_sig = set(inspect.signature(func).parameters)
        input_names = set(fields.keys())
        missing = func_sig.difference(input_names)
        extra = input_names.difference(func_sig)
        if missing:
            raise ContractError("Missing description of arguments '{}'".format(missing))
        if extra:
            raise ContractError("Description of non-existent arguments '{}'".format(extra))
        func._serving_inputs = fields
        return func
    return dec

def outputs(**fields):
    def dec(func):
        func._serving_outputs = fields
        return func
    return dec
