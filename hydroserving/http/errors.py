class BackendException(RuntimeError):
    def __init__(self, details):
        message = "Server returned an error: " + str(details)
        super().__init__(message)
