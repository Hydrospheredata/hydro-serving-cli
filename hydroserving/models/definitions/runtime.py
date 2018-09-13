class Runtime:
    def __init__(self, name, version, model_type, tags, config_params):
        """

        Args:
            config_params (dict):
            tags (list of str):
            model_type (str):
            name (str):
            version (str):
        """
        self.config_params = config_params
        self.name = name
        self.version = "latest" if version is None else version
        self.model_type = model_type
        self.tags = tags
