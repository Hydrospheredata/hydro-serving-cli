class HSApiError(RuntimeError):
    pass


class ResponseIsNotJson(HSApiError):
    pass
