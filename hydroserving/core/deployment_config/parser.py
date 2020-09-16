import copy

from hydrosdk import DeploymentConfiguration


def parse_deployment_configuration(in_dict) -> DeploymentConfiguration:
    new_in_dict = copy.deepcopy(in_dict)
    del new_in_dict['kind']
    return DeploymentConfiguration.from_camel_case_dict(new_in_dict)
