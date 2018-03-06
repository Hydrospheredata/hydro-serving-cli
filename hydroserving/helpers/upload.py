from hydroserving.httpclient.api import UploadMetadata
from hydroserving.helpers.assembly import assemble_model
from hydroserving.models.model_metadata import ModelMetadata
import click


def upload_model(model_api, source, model):
    tar = assemble_model(model)
    model_metadata = ModelMetadata.from_folder_metadata(model)

    click.echo("Uploading {} to {}".format(tar, model_api.connection.remote_addr))

    metadata = UploadMetadata(
        model_name=model_metadata.model_name,
        model_type=model_metadata.model_type,
        target_source=source,
        model_contract=model_metadata.model_contract.SerializeToString(),
        description=model_metadata.description
    )

    return model_api.upload(tar, metadata)
