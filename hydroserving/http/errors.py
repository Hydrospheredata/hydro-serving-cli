class HSApiError(RuntimeError):
    def __init__(self, msg, details = None):
        message = "Server returned an error: " + str(details)
        super().__init__(message)


class ResponseIsNotJson(HSApiError):
    def __init__(self, response):
        message = "[" + str(response.status_code) + "]: " + response.text
        super().__init__(message)
        self.response = response

