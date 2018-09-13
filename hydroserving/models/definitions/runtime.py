class Runtime:
    def __init__(self, name, version, model_type, **kwargs):
        """

        Args:
            name (str):
            version (str):
        """
        self.repository = name
        self.version = "latest" if version is None else version
        self.model_type = model_type
        self.misc = kwargs
