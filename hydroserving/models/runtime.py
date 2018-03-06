class Runtime:
    def __init__(self, repository, tag):
        self.repository = repository
        self.tag = "latest" if tag is None else tag

    def __str__(self):
        return "{}:{}".format(self.repository, self.tag)

    @staticmethod
    def from_dict(data_dict):
        if data_dict is None:
            return None
        return Runtime(
            repository=data_dict.get("repository"),
            tag=data_dict.get("tag")
        )
