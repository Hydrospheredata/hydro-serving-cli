class ConfigurationError(Exception):
    pass


class ParseConfigurationError(ConfigurationError):
    pass


class ClusterNotFoundError(ConfigurationError):
    pass

class ClusterAlreadyExistsError(ConfigurationError):
    pass 