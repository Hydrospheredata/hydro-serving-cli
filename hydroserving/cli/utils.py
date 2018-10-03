import click
import os

from hydroserving.helpers.contract import read_contract_file
from hydroserving.helpers.file import get_yamls, get_visible_files
from hydroserving.models.definitions.model import Model
from hydroserving.parsers.model import ModelParser


def ensure_config(obj):
    return ensure(obj, "config", "hs config is not found")


def ensure_cluster(obj):
    maybe_result = obj.services.config.current_cluster()
    if maybe_result is None:
        click.echo("No current cluster. Check it with `hs cluster` command")
        raise SystemExit(-1)
    return maybe_result


def ensure_app_data(obj):
    return ensure(obj, "app_data", "Directory doesn't have an application data")


def ensure_kafka_params(obj):
    return ensure(obj, "kafka_params", "Kafka params aren't specified")


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


def ensure_model(obj, path, name, model_type, description, contract):
    serving_files = [
        file
        for file in get_yamls(path)
        if os.path.splitext(os.path.basename(file))[0] == "serving"
    ]
    serving_file = serving_files[0] if serving_files else None

    if len(serving_files) > 1:
        click.echo("Warning: multiple serving files. Using {}".format(serving_file))

    metadata = None
    if serving_file is not None:
        metadata = ModelParser().parse_yaml(serving_file)

    if metadata is None:
        external_contract = None
        if contract is not None:
            external_contract = read_contract_file(contract)

        metadata = Model(
            name=name,
            model_type=model_type,
            contract=external_contract,
            description=description,
            payload=['.']
        )

    obj.model = metadata
    return metadata
