import logging
import os
import sys
from typing import Callable, Any

from hydroserving.config.parser import parse_config
from hydroserving.core.application.parser import parse_application
from hydroserving.core.application.service import ApplicationService
from hydroserving.core.deployment_config.parser import parse_deployment_configuration
from hydroserving.core.deployment_config.service import DeploymentConfigurationService
from hydroserving.core.model.parser import parse_model, parse_metrics
from hydroserving.core.model.service import ModelService
from hydroserving.util.fileutil import get_yamls, is_yaml
from hydroserving.util.yamlutil import yaml_file_stream
from hydroserving.core.apply.context import ApplyContext


class ApplyService:
    def __init__(self,
                 model_service: ModelService,
                 application_service: ApplicationService,
                 deployment_configuration_service: DeploymentConfigurationService):
        """

        Args:
            application_service (ApplicationService):
            model_service (ModelService):
        """
        self.apply_context = ApplyContext()
        self.application_service = application_service
        self.model_service = model_service
        self.deployment_configuration_service = deployment_configuration_service

    def apply(self, paths, recursive, **kwargs):
        """

        Args:
            paths (list of str):

        Returns:
            list of dict:
        """
        results = {}
        for path in paths:
            if path == "<STDIN>":  # special case for stdin redirect
                logging.info("Reading resource from <STDIN>")
                results[os.getcwd()] = yaml_file_stream(sys.stdin)
            else:
                abspath = os.path.abspath(path)
                if not os.path.exists(abspath):
                    raise FileNotFoundError(path)
                if os.path.isdir(abspath):
                    logging.debug(f"Detected a directory {abspath}, looking for resources")
                    for yaml_file in sorted(get_yamls(abspath, recursive)):
                        logging.info("Reading {}".format(yaml_file))
                        with open(yaml_file, 'r') as f:
                            results[yaml_file] = yaml_file_stream(f)
                elif is_yaml(abspath):
                    logging.info("Reading {}".format(abspath))
                    with open(abspath, 'r') as f:
                        results[abspath] = yaml_file_stream(f)
                else:
                    raise UnknownFile(file)
        for source, docs in results.items():
            results[source] = self.apply_yaml(docs, source, **kwargs)
        return results

    def apply_yaml(self, docs, path, **kwargs):
        responses = []
        for doc_obj in docs:
            kind = doc_obj.get("kind")
            if not kind:
                logging.warning(f"Couldn't find resource specification (kind) at {path}, skipping")
                continue
            if kind == 'Model':
                logging.debug("Model detected")
                model_folder_path = path if os.path.isdir(path) else os.path.dirname(path)
                model_version = self.model_service.apply(
                    parse_model(doc_obj), 
                    parse_metrics(doc_obj), 
                    model_folder_path,
                    self.apply_context,
                    **kwargs)
                self.apply_context.add_model_version(model_version)
                responses.append(model_version)
            elif kind == 'Application':
                logging.debug("Application detected")
                partial_application_parser = parse_application(doc_obj)
                application = self.application_service.apply(
                    partial_application_parser,
                    self.apply_context,
                    **kwargs)
                self.apply_context.add_application(application)
                responses.append(application)
            elif kind == 'DeploymentConfiguration':
                logging.debug("DeploymentConfiguration detected")
                partial_dc_parser = parse_deployment_configuration(doc_obj)
                config = self.deployment_configuration_service.apply(
                    partial_dc_parser,
                    self.apply_context,
                    **kwargs)
                self.apply_context.add_deployment_configuration(config)
                responses.append(config)
            else:
                logging.warning("Unknown resource: {}, skipping".format(doc_obj))
                continue
        return responses


class ApplyError(RuntimeError):
    pass


class UnknownResource(ApplyError):
    def __init__(self, res):
        super().__init__("Unknown resource: {}".format(res))


class UnknownFile(ApplyError):
    def __init__(self, path):
        super().__init__(path, "File is not supported: {}".format(path))
