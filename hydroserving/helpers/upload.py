from hydroserving.httpclient.api import UploadMetadata
from hydroserving.helpers.assembly import assemble_model
from hydroserving.models.model_metadata import ModelMetadata
import click


def upload_model(model_api, source, model):
    tar = assemble_model(model)
    model_metadata = ModelMetadata.from_folder_metadata(model)

    click.echo("Uploading to {}".format(model_api.connection.remote_addr))

    contract = None
    if model_metadata.model_contract is not None:
        contract = model_metadata.model_contract.SerializeToString()

    metadata = UploadMetadata(
        model_name=model_metadata.model_name,
        model_type=model_metadata.model_type,
        target_source=source,
        model_contract=contract,
        description=model_metadata.description
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
