import click
import os
import yaml
from hydroserving.helpers.file import get_visible_files, get_yamls
from hydroserving.models.definitions.model import Model
from hydroserving.models.context_object import ContextObject


@click.group()
@click.version_option(message="%(prog)s version %(version)s")
@click.option('--name',
              default=os.path.basename(os.getcwd()),
              show_default=True,
              required=False)
@click.option('--model_type',
              default="unknown",
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
    cwd = os.getcwd()
    serving_files = [
        file
        for file in get_yamls(cwd)
        if os.path.splitext(os.path.basename(file))[0] == "serving"
    ]
    serving_file = serving_files[0] if serving_files else None

    if len(serving_files) > 1:
        click.echo("Warning: multiple serving files. Using {}".format(serving_file))

    metadata = None
    if serving_file is not None:
        with open(serving_file, "r") as file:
            serving_content = yaml.load(file)
            print(serving_content)
            metadata = Model.from_dict(serving_content)

    if metadata is None:
        metadata = Model(
            name=name,
            model_type=model_type,
            contract=None,
            description=description,
            payload=get_visible_files('.')
        )
    ctx.obj.metadata = metadata
