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
        self.application_service = application_service
        self.model_service = model_service
        self.deployment_configuration_service = deployment_configuration_service

    def apply(self, paths, **kwargs):
        """

        Args:
            paths (list of str):

        Returns:
            list of dict:
        """
        results = {}
        for file in paths:
            abs_file = os.path.abspath(file)
            if file == "<STDIN>":  # special case for stdin redirect
                logging.info("Reading resource from <STDIN>")
                results[os.getcwd()] = yaml_file_stream(sys.stdin)
            else:
                if not os.path.exists(file):
                    raise FileNotFoundError(file)

                if os.path.isdir(file):
                    logging.debug("Looking for resources in {}".format(os.path.basename(abs_file)))
                    for yaml_file in sorted(get_yamls(abs_file)):
                        logging.info("Reading {}".format(os.path.basename(yaml_file)))
                        with open(yaml_file, 'r') as f:
                            results[abs_file] = yaml_file_stream(f)
                elif is_yaml(file):
                    logging.info("Reading {}".format(os.path.basename(file)))
                    with open(file, 'r') as f:
                        results[os.path.dirname(abs_file)] = yaml_file_stream(f)
                else:
                    raise UnknownFile(file)

        for source, docs in results.items():
            results[source] = self.apply_yaml(docs, source, **kwargs)
        return results

    def apply_yaml(self, docs, call_path, **kwargs):
        responses = []
        for doc_obj in docs:
            kind = doc_obj.get("kind")
            if not kind:
                logging.error("Cannot parse a resource without `kind` specification")
                raise SystemExit(1)
            if kind == 'Model':
                logging.debug("Model detected")
                responses.append(self.model_service.apply(
                    parse_model(doc_obj), 
                    parse_metrics(doc_obj), 
                    call_path, **kwargs
                ))
            elif kind == 'Application':
                logging.debug("Application detected")
                partial_application_parser = parse_application(doc_obj)
                responses.append(self.application_service.apply(
                    partial_application_parser
                ))
            elif kind == 'DeploymentConfiguration':
                logging.debug("DeploymentConfiguration detected")
                partial_dc_parser = parse_deployment_configuration(doc_obj)
                responses.append(self.deployment_configuration_service.apply(
                    partial_dc_parser
                ))
            else:
                logging.error("Unknown resource: {}".format(doc_obj))
                raise UnknownResource(doc_obj)
        return responses


class ApplyError(RuntimeError):
    pass


class UnknownResource(ApplyError):
    def __init__(self, res):
        super().__init__("Unknown resource: {}".format(res))


class UnknownFile(ApplyError):
    def __init__(self, path):
        super().__init__(path, "File is not supported: {}".format(path))
