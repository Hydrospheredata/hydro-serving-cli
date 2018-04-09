from hydroserving.helpers.deployment import *
from hydroserving.models import FolderMetadata
from hydroserving.models.context_object import ContextObject


@click.group()
@click.pass_context
def hs_cli(ctx):
    ctx.obj = ContextObject()
    metadata = FolderMetadata.from_directory(os.getcwd())
    ctx.obj.metadata = metadata
