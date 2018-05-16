from hydroserving.helpers.deployment import *
from hydroserving.models import FolderMetadata, ModelDefinition, LocalDeployment
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
            payload=[os.path.join(dir_name, file) for dir_name, _, files in os.walk('.') for file in files if not dir_name.startswith("./target")]
        ), None)
    ctx.obj.metadata = metadata
