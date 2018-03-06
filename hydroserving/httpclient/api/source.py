class SourceAPI:
    def __init__(self, connection):
        self.connection = connection

    def list(self):
        return self.connection.get("/api/v1/modelSource")
