import click
import os

from hydroserving.core.contract import read_contract_file
from hydroserving.core.model.model import Model
from hydroserving.core.parsers.model import ModelParser
from hydroserving.filesystem.utils import get_yamls


def ensure_config(obj):
    return ensure(obj, "config", "hs config is not found")


def ensure_config(obj):
    maybe_result = obj.services.config
    if maybe_result is None:
        click.echo("No configuration. Check it with `hs cluster` command")
        raise SystemExit(-1)
    return maybe_result


def ensure_app_data(obj):
    return ensure(obj, "app_data", "Directory doesn't have an application data")


def ensure(obj, obj_field, error_msg=None):
    maybe_result = try_get(obj, obj_field)
    if maybe_result is None:
        if error_msg is None:
            click.echo("Can't find {} in context object".format(obj_field))
        else:
            click.echo(error_msg)
        raise SystemExit(-1)
    return maybe_result


def try_get(obj, obj_field):
    return obj.__dict__[obj_field]


def ensure_model(dir_path, name, runtime, host_selector, path_to_training_data):
    """

    Args:
        host_selector (str):
        runtime (str):
        dir_path (str):
        name (str):
        path_to_training_data (str or None):

    Returns:
        Model:
    """
    serving_files = [
        file
        for file in get_yamls(dir_path)
        if os.path.splitext(os.path.basename(file))[0] == "serving"
    ]
    serving_file = serving_files[0] if serving_files else None

    if len(serving_files) > 1:
        click.echo("Warning: multiple serving files. Using {}".format(serving_file))

    metadata = None
    if serving_file is not None:
        metadata = ModelParser().parse_yaml(serving_file)
        if name is not None:
            metadata.name = name
        if runtime is not None:
            metadata.runtime = runtime
        if host_selector is not None:
            metadata.host_selector = host_selector
        if path_to_training_data is not None:
            metadata.training_data_file = path_to_training_data

    if metadata is None:
        if name is None:
            name = os.path.basename(os.getcwd())
        metadata = Model(
            name=name,
            contract=None,
            runtime=runtime,
            host_selector=host_selector,
            payload=[os.path.join(dir_path, "*")],
            training_data_file=path_to_training_data,
            install_command=None
        )

    resolve_model_paths(dir_path, metadata)

    return metadata


def resolve_model_paths(dir_path, model):
    """

    Args:
        dir_path (str): path to dir with metadata
        model (Model):

    Returns:
        Model: with resolved payload paths
    """
    abs_payload_paths = []
    for p in model.payload:
        if not os.path.isabs(p):
            p = os.path.normpath(os.path.join(dir_path, p))
        abs_payload_paths.append(p)

    model.payload = abs_payload_paths
    return model
