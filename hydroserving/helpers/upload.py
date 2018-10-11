import time

import click

from hydroserving.httpclient.api import UploadMetadata, ModelAPI
from hydroserving.helpers.package import assemble_model
from hydroserving.models.definitions.model import Model


class ModelBuildError(RuntimeError):
    pass


def await_upload(model_api, build_status):
    is_finished = False
    is_failed = False
    while not (is_finished or is_failed):
        build_status = model_api.build_status(str(build_status['id']))
        is_finished = build_status['status'] == 'Finished'
        is_failed = build_status['status'] == 'Failed'
        time.sleep(5)  # wait until it's finished

    if is_failed:
        raise ModelBuildError(build_status)

    return build_status


def await_training_data(profile_api, uid):
    status = ""
    while status != "success":
        status = profile_api.status(uid)
        time.sleep(30)
    return uid


def push_training_data_async(profile_api, model_version_id, filename):
    with click.progressbar(length=1, label='Uploading training data') as bar:
        uid = profile_api.push(model_version_id, filename, create_bar_callback_factory(bar))
    click.echo()
    click.echo("Data profile computing is started with id {}".format(uid))
    return uid


def push_training_data(profile_api, model_version_id, filename, is_async):
    uid = push_training_data_async(profile_api, model_version_id, filename)

    if is_async:
        return uid
    else:
        return await_training_data(profile_api, uid)


def upload_model_async(model_api, model, target_path):
    """

    Args:
        target_path (str):
        model_api (ModelAPI):
        model (Model):

    Returns:
        dict:
    """
    tar = assemble_model(model, target_path)

    click.echo("Uploading to {}".format(model_api.connection.remote_addr))

    contract = None
    if model.contract is not None:
        contract = model.contract.SerializeToString()

    metadata = UploadMetadata(
        model_name=model.name,
        model_type=model.model_type,
        model_contract=contract,
        description=model.description
    )

    with click.progressbar(length=1, label='Uploading model assembly')as bar:
        create_encoder_callback = create_bar_callback_factory(bar)
        result = model_api.upload(tar, metadata, create_encoder_callback)

    return result


def upload_model(model_api, profiler_api, model, target_path, is_async):
    build_status = upload_model_async(model_api, model, target_path)

    push_uid = None

    if model.training_data_file is not None:
        model_version = build_status['id']
        push_uid = push_training_data_async(profiler_api, model_version, model.training_data_file)

    if is_async:
        return build_status
    else:
        build_status = await_upload(model_api, build_status)
        if push_uid is not None:
            push_uid = await_training_data(profiler_api, push_uid)
        return build_status


def create_bar_callback_factory(bar):
    def create_click_callback(multipart_encoder):
        bar.length = multipart_encoder.len

        def callback(monitor):
            bar.update(monitor.bytes_read)

        return callback

    return create_click_callback
