from hydrosdk import DeploymentConfiguration


def parse_deployment_configuration(in_dict):
    if in_dict is None:
        return None
    del in_dict['kind']
    return DeploymentConfiguration.from_camel_case_dict(in_dict)

