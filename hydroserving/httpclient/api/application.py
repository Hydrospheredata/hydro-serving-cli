class ApplicationAPI:
    def __init__(self, connection):
        self.connection = connection

    def create(self, application):
        return self.connection.post("/api/v1/applications", application)

    def serve(self, app_name, signature, data):
        return self.connection.post(
            '/api/v1/applications/serve/{0}/{1}'.format(app_name, signature),
            data
        )
