import logging
from typing import Optional, Union, List, Iterable
from collections import deque

from hydrosdk.modelversion import ModelVersion
from hydrosdk.application import Application
from hydrosdk.deployment_configuration import DeploymentConfiguration


def valid_reference(func):
    def inner(self, reference):
        p1 = reference.startswith("{{this.")
        p2 = reference.endswith("}}")
        p3 = reference.startswith("{{this.model")
        p4 = reference.startswith("{{this.application")
        p5 = reference.startswith("{{this.deployment_configuration")
        valid = (p1 and p2) and (p3 or p4 or p5)
        return func(self, reference) if valid else func(self, None)
    return inner


class ApplyContext:
    def __init__(self) -> 'ApplyContext':
        self.model_versions = deque()
        self.applications = deque()
        self.deployment_configurations = deque()

    def add_model_version(self, model_version: ModelVersion):
        self.model_versions.appendleft(model_version)
    
    def add_application(self, application: Application):
        self.applications.appendleft(application)
    
    def add_deployment_configuration(self, config: DeploymentConfiguration):
        self.deployment_configurations.appendleft(config)
    
    @staticmethod
    def _search_candidate(reference: str, collection: Iterable) -> List[Union[ModelVersion, Application, DeploymentConfiguration]]:
        return list(filter(lambda x: x.name == reference, collection))

    @valid_reference
    def parse_model_version(self, reference: Optional[str]) -> Optional[ModelVersion]:
        logging.debug(f"Looking for reference={reference} in apply context")
        result = None
        template = "{{this.model."
        if reference is not None and reference.startswith(template):
            raw_reference = reference[len(template):-2]
            template_version = None
            try: 
                name, version = raw_reference.split(':')
                template_version = int(version)
                candidates = self._search_candidate(name, self.model_versions)
                if template_version > len(candidates):
                    logging.error(f"Invalid template reference for model version, required "
                        f"version: {template_version}; found {len(candidates)} candidates.")
                    raise SystemExit(1)
                result = candidates[template_version]
            except ValueError as e:
                result = self._search_candidate(raw_reference, self.model_versions)[0]
            except IndexError as e:
                logging.error(f"Couldn't reference candidate using index: {template_version}")
                raise SystemExit(1)
        if result is not None:
            logging.debug(f"Found substitution candidate from context: {repr(result)}")
        return result
        
    @valid_reference
    def parse_application(self, reference: Optional[str]) -> Optional[Application]:
        result = None
        template = "{{this.application."
        if reference is not None and reference.startswith(template):
            raw_reference = reference[len(template):-2]
            candidates = self._search_candidate(raw_reference, self.applications)
            if candidates:
                result = candidates[0]
        if result is not None:
            logging.debug(f"Found substitution candidate from context: {repr(result)}")
        return result

    @valid_reference
    def parse_deployment_configuration(self, reference: Optional[str]) -> Optional[DeploymentConfiguration]:
        result = None
        template = "{{this.application."
        if reference is not None and reference.startswith(template):
            raw_reference = reference[len(template):-2]
            candidates = self._search_candidate(raw_reference, self.deployment_configurations)
            if candidates:
                result = candidates[0]
        if result is not None:
            logging.debug(f"Found substitution candidate from context: {repr(result)}")
        return result

    def to_dict(self):
        return {
            "model_versions": [repr(item) for item in self.model_versions],
            "applications": [repr(item) for item in self.applications],
            "deployment_configurations": [repr(item) for item in self.deployment_configurations]
        }
