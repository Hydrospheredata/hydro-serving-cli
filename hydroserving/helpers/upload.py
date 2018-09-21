import click

from hydroserving.httpclient.api import UploadMetadata, ModelAPI
from hydroserving.helpers.package import assemble_model
from hydroserving.models.definitions.model import Model


def upload_model(model_api, model, target_path):
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


def create_bar_callback_factory(bar):
    def create_click_callback(multipart_encoder):
        bar.length = multipart_encoder.len

        def callback(monitor):
            bar.update(monitor.bytes_read)

        return callback

    return create_click_callback
