class Environment:
    def __init__(self, name, selector):
        """

        Args:
            name (str): name of environment
            selector (str): json-like env selector
        """
        self.name = name
        self.selector = selector
