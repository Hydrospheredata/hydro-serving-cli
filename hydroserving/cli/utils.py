import click


def ensure_metadata(obj):
    return ensure(obj, "metadata", "Directory doesn't have a serving metadata")

def get_metadata(obj):
    return try_get(obj, "metadata")

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
