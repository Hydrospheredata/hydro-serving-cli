import logging
import os
import sys

from hydroserving.config.parser import parse_config
from hydroserving.core.application.parser import parse_application
from hydroserving.core.application.service import ApplicationService
from hydroserving.core.host_selector.parser import parse_host_selector
from hydroserving.core.model.parser import parse_model
from hydroserving.core.model.service import ModelService
from hydroserving.util.fileutil import get_yamls, is_yaml
from hydroserving.util.yamlutil import yaml_file_stream

KIND_TO_PARSER = {
    "Config": parse_config,
    "Model": parse_model,
    "HostSelector": parse_host_selector,
    "Application": parse_application
}


def parse_generic_dict(in_dict):
    kind = in_dict.get("kind")
    if not kind:
        raise ValueError("Cannot parse resource without kind")
    parser = KIND_TO_PARSER.get(kind)
    if parser is None:
        raise ValueError("No parser found for resource kind {}".format(kind))
    return parser(in_dict)


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
                logging.info("Reading resource from <STDIN> ...")
                results[os.getcwd()] = yaml_file_stream(sys.stdin)
            else:
                if not os.path.exists(file):
                    raise FileNotFoundError(file)

                if os.path.isdir(file):
                    logging.debug("Looking for resources in {} ...".format(os.path.basename(abs_file)))
                    for yaml_file in sorted(get_yamls(abs_file)):
                        logging.info("Reading {} ...".format(os.path.basename(yaml_file)))
                        with open(yaml_file, 'r') as f:
                            results[file] = yaml_file_stream(f)
                elif is_yaml(file):
                    logging.info("Reading {} ...".format(os.path.basename(file)))
                    with open(file, 'r') as f:
                        results[os.path.dirname(file)] = yaml_file_stream(f)
                else:
                    raise UnknownFile(file)

        for source, docs in results.items():
            results[source] = self.apply_yaml(docs, source, **kwargs)
        return results

    def apply_yaml(self, docs, call_path, **kwargs):
        responses = []
        for doc_obj in docs:
            parsed = parse_generic_dict(doc_obj)
            kind = doc_obj.get('kind')
            if kind is None:
                raise ValueError("Resource kind is not specified.")
            if kind == 'Model':
                logging.debug("Model detected")
                responses.append(self.model_service.apply(parsed, call_path, **kwargs))
            elif kind == 'Application':
                logging.debug("Application detected")
                responses.append(self.application_service.apply(parsed))
            elif kind == 'HostSelector':
                logging.debug("HostSelector detected")
                responses.append(self.selector_service.apply(parsed))
            else:
                logging.error("Unknown resource: {}".format(parsed))
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
