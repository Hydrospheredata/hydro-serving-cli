import logging
from urllib.parse import urljoin

import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder

from hydroserving.http.errors import BackendException
from hydroserving.util.dictutil import remove_none


class RemoteConnection:
    def __init__(self, remote_addr):
        self.remote_addr = remote_addr

    def compose_url(self, url):
        full_url = urljoin(self.remote_addr, url)
        return full_url

    def post(self, url, data):
        """
        Sends POST request with `data` to the given `url` and returns data as JSON dictionary.
        """
        data = self.preprocess_request(data)
        result = requests.post(self.compose_url(url), json=data)
        return RemoteConnection.postprocess_response(result)

    def put(self, url, data):
        """
        Sends PUT request with `data` to the given `url` and returns data as JSON dictionary.
        """
        data = self.preprocess_request(data)
        result = requests.put(self.compose_url(url), json=data)
        return RemoteConnection.postprocess_response(result)

    def get(self, url):
        """
        Sends GET request with to the given `url` and returns data as JSON dictionary.
        Returns (requests.Response)
        """
        result = requests.get(self.compose_url(url))
        return RemoteConnection.postprocess_response(result)

    def delete(self, url):
        """
        Sends DELETE request with to the given `url` and returns data as JSON dictionary.
        """
        result = requests.delete(self.compose_url(url))
        return RemoteConnection.postprocess_response(result)

    def multipart_post(self, url, data, files):
        fields = {**self.preprocess_request(data), **files}
        logging.debug("Multipart request. Parts: %s", fields)
        encoder = MultipartEncoder(
            fields=fields
        )

        result = requests.post(
            url=self.compose_url(url),
            data=encoder,
            headers={'Content-Type': encoder.content_type}
        )

        return RemoteConnection.postprocess_response(result)

    @staticmethod
    def preprocess_request(request):
        return remove_none(request)

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
