import os

import click

from hydroserving.constants.package import TARGET_FOLDER
from hydroserving.helpers.file import is_yaml, get_yamls
from hydroserving.helpers.upload import upload_model
from hydroserving.httpclient.api import ModelAPI
from hydroserving.services.client import HttpService
from hydroserving.models.definitions.environment import Environment
from hydroserving.models.definitions.application import Application
from hydroserving.models.definitions.model import Model
from hydroserving.models.definitions.runtime import Runtime
from hydroserving.parsers.generic import GenericParser


class ApplyService:
    def __init__(self, http_service):
        """

        Args:
            http_service (HttpService): http client to access the cluster
        """
        self.http = http_service
        self.parser = GenericParser()

    def apply(self, paths):
        """

        Args:
            paths (list of str):

        Returns:
            list of dict:
        """
        results = {}
        for file in paths:
            abs_file = os.path.abspath(file)
            if os.path.isdir(file):
                click.echo("Looking for resources in {} ...".format(os.path.basename(abs_file)))
                for yaml_file in sorted(get_yamls(abs_file)):
                    yaml_res = self.apply_yaml(yaml_file)
                    results[file] = yaml_res
            elif is_yaml(file):
                yaml_res = self.apply_yaml(abs_file)
                results[file] = yaml_res
            else:
                raise UnknownFile(file)
        return results

    def apply_yaml(self, path):
        click.echo("Applying {} ...".format(os.path.basename(path)))
        responses = []
        for doc_obj in self.parser.parse_yaml_stream(path):
            if isinstance(doc_obj, Model):
                responses.append(self.apply_model(doc_obj, path))
            elif isinstance(doc_obj, Runtime):
                responses.append(self.apply_runtime(doc_obj))
            elif isinstance(doc_obj, Application):
                responses.append(self.apply_application(doc_obj))
            elif isinstance(doc_obj, Environment):
                responses.append(self.apply_environment(doc_obj))
            else:
                raise UnknownResource(doc_obj, path)
        return responses

    def apply_model(self, model, path):
        model_api = ModelAPI(self.http.connection())
        folder = os.path.abspath(os.path.dirname(path))
        target_path = os.path.join(folder, TARGET_FOLDER)
        return upload_model(model_api, model, target_path)

    def apply_runtime(self, runtime):
        pass

    def apply_environment(self, env):
        pass

    def apply_application(self, app):
        pass


class ApplyError(RuntimeError):
    def __init__(self, path, msg):
        super().__init__(msg)
        self.file = path


class UnknownResource(ApplyError):
    def __init__(self, res, path):
        super().__init__(path, "Unknown resource: {}".format(res))
        self.resource = res


class UnknownFile(ApplyError):
    def __init__(self, path):
        super().__init__(path, "File is not supported: {}".format(path))
