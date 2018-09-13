class RuntimeAPI:
    def __init__(self, connection):
        self.connection = connection

    def create(self, name, version, rtypes, tags=None, config_params=None):
        """
        Create a runtime
        Args:
            name (str):
            version (str):
            rtypes (list of str):
            tags (list of str):
            config_params (dict):

        Returns:
            dict:

        """
        if config_params is None:
            config_params = {}
        if tags is None:
            tags = []
        data = {
            "name": name,
            "version": version,
            "modelTypes": rtypes,
            "tags": tags,
            "configParams": config_params
        }
        return self.connection.post("/api/v1/runtime", data)

    def list(self):
        """
        Return all runtimes
        Returns:
            list of dict
        """
        return self.connection.get("/api/v1/runtime")

    def find(self, name, version):
        """
        Find a runtime
        Args:
            name (str):
            version (str):

        Returns:
            dict: if found
            None: otherwise
        """
        for runtime in self.list():
            if runtime["name"] == name and runtime["version"] == version:
                return runtime
        return None

    def get_status(self, request_id):
        """

        Args:
            request_id (int):

        Returns:
            dict:
        """
        return self.connection.get("/api/v1/runtime/status/" + str(request_id))