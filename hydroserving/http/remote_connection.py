import logging
from urllib.parse import urljoin

import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder

from hydroserving.util.dictutil import remove_none


class BackendException(RuntimeError):
    def __init__(self, details):
        message = "Server returned an error: " + str(details)
        super().__init__(message)


class RemoteConnection:
    def __init__(self, remote_addr):
        self.remote_addr = remote_addr

    def compose_url(self, url):
        full_url = urljoin(self.remote_addr, url)
        return full_url

    def post_stream(self, url, data):
        """
        Sends POST request with `data` to the given `url` and returns data as JSON dictionary.
        """
        composed = self.compose_url(url)
        result = requests.post(composed, data=data, stream=True)
        logging.debug(result.request.__dict__)
        return RemoteConnection.postprocess_response(result)

    def post_json(self, url, data):
        """
        Sends POST request with `data` to the given `url` and returns data as JSON dictionary.
        """
        composed = self.compose_url(url)
        result = requests.post(composed, json=data)
        return RemoteConnection.postprocess_response(result)

    def put(self, url, data):
        """
        Sends PUT request with `data` to the given `url` and returns data as JSON dictionary.
        """
        composed = self.compose_url(url)
        result = requests.put(composed, json=data)
        return RemoteConnection.postprocess_response(result)

    def get(self, url):
        """
        Sends GET request with to the given `url` and returns data as JSON dictionary.
        Returns (requests.Response)
        """
        composed = self.compose_url(url)
        result = requests.get(composed)
        return RemoteConnection.postprocess_response(result)

    def delete(self, url):
        """
        Sends DELETE request with to the given `url` and returns data as JSON dictionary.
        """
        composed = self.compose_url(url)
        result = requests.delete(composed)
        return RemoteConnection.postprocess_response(result)

    def multipart_post(self, url, data, files):
        fields = {**data, **files}
        composed = self.compose_url(url)
        logging.debug("MULTIPART POST: %s. Parts: %s", composed, fields)
        encoder = MultipartEncoder(
            fields=fields
        )

        result = requests.post(
            url=composed,
            data=encoder,
            headers={'Content-Type': encoder.content_type}
        )

        return RemoteConnection.postprocess_response(result)

    @staticmethod
    def postprocess_response(response):
        """

            Args:
                response (requests.Response):

            Returns:

            """
        if 500 <= response.status_code < 600:
            logging.error("Got server error %s", response)
            raise BackendException(response.content.decode('utf-8'))
        return response
