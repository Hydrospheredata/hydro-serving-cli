from hydroserving.helpers.assembly import assemble_model
from hydroserving.models.model_metadata import ModelMetadata
import click
import requests


def upload_model(host, port, source, model):
    tar = assemble_model(model)
    model_metadata = ModelMetadata.from_folder_metadata(model)
    addr = "http://{}:{}/api/v1/model".format(host, port)
    click.echo("Uploading {} to {}".format(tar, addr))
    data_dict = model_metadata.to_upload_data()
    data_dict["target_source"] = source
    result = requests.post(
        addr,
        data=data_dict,
        files={"payload": open(tar, "rb")}
    )
    return result
