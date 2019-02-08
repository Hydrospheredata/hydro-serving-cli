import logging
import os
import sys

from hydroserving.core.application.service import ApplicationService
from hydroserving.core.host_selector.host_selector import HostSelector
from hydroserving.core.model.service import ModelService
from hydroserving.core.application.entities import Application
from hydroserving.core.model.entities import Model
from hydroserving.core.parsers.generic_parser import GenericParser
from hydroserving.util.fileutil import get_yamls, is_yaml


class ApplyService:
    def __init__(self, model_service, selector_service, application_service):
        """

        Args:
            application_service (ApplicationService):
            selector_service (HostSelectorService):
            model_service (ModelService):
        """
        self.application_service = application_service
        self.selector_service = selector_service
        self.model_service = model_service
        self.parser = GenericParser()

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
                logging.info("Applying resource from <STDIN> ...")
                yaml_res = self.apply_yaml(sys.stdin, **kwargs)
                results[file] = yaml_res
            elif os.path.isdir(file):
                logging.debug("Looking for resources in {} ...".format(os.path.basename(abs_file)))
                for yaml_file in sorted(get_yamls(abs_file)):
                    logging.info("Applying {} ...".format(os.path.basename(yaml_file)))
                    with open(yaml_file, 'r') as f:
                        yaml_res = self.apply_yaml(f, **kwargs)
                        results[yaml_file] = yaml_res
            elif is_yaml(file):
                logging.info("Applying {} ...".format(os.path.basename(file)))
                with open(file, 'r') as f:
                    yaml_res = self.apply_yaml(f, **kwargs)
                    results[file] = yaml_res
            else:
                raise UnknownFile(file)
        return results

    def apply_yaml(self, file, **kwargs):
        responses = []
        stream = self.parser.yaml_file_stream(file)
        for doc_obj in stream:
            if isinstance(doc_obj, Model):
                logging.debug("Model detected")
                responses.append(self.model_service.apply(doc_obj, file))
            elif isinstance(doc_obj, Application):
                logging.debug("Application detected")
                responses.append(self.application_service.apply(doc_obj, **kwargs))
            elif isinstance(doc_obj, HostSelector):
                logging.debug("HostSelector detected")
                responses.append(self.selector_service.apply(doc_obj))
            else:
                logging.error("Unknown resource: {}".format(doc_obj))
                raise UnknownResource(doc_obj)
        return responses


class ApplyError(RuntimeError):
    pass


class UnknownResource(ApplyError):
    def __init__(self, res):
        super().__init__("Unknown resource: {}".format(res))
        self.resource = res


class UnknownFile(ApplyError):
    def __init__(self, path):
        super().__init__(path, "File is not supported: {}".format(path))