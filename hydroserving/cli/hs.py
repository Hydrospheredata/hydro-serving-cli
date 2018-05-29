import click

from hydroserving.helpers.deployment import *
from hydroserving.helpers.package import get_visible_files
from hydroserving.models import FolderMetadata, ModelDefinition
from hydroserving.models.context_object import ContextObject


@click.group()
@click.option('--name',
              default=os.path.basename(os.getcwd()),
              show_default=True,
              required=False)
@click.option('--model_type',
              default=None,
              required=False)
@click.option('--contract',
              type=click.Path(exists=True),
              default=None,
              required=False)
@click.option('--description',
              default=None,
              required=False)
@click.pass_context
def hs_cli(ctx, name, model_type, contract, description):
    ctx.obj = ContextObject()
    metadata = FolderMetadata.from_directory(os.getcwd())
    if metadata is None:
        metadata = FolderMetadata(ModelDefinition(
            name=name,
            model_type=model_type,
            contract_path=contract,
            description=description,
            payload=get_visible_files('.')
        ), None)
    ctx.obj.metadata = metadata
