from json import JSONDecodeError
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder, MultipartEncoderMonitor

from hydroserving.httpclient.errors import ResponseIsNotJson, HSApiError


class RemoteConnection:
    def __init__(self, remote_addr):
        self.remote_addr = remote_addr

    def compose_url(self, url):
        full_url = self.remote_addr + url
        return full_url

    def post(self, url, data):
        """
        Sends POST request with `data` to the given `url` and returns data as JSON dictionary.
        """
        result = requests.post(self.compose_url(url), json=data)
        return self.postprocess_response(result)

    def get(self, url):
        """
        Sends GET request with to the given `url` and returns data as JSON dictionary.
        """
        result = requests.get(self.compose_url(url))
        return self.postprocess_response(result)

    def multipart_post(self, url, data, files, create_encoder_callback=None):
        encoder = MultipartEncoder(
            fields={**data, **files}
        )

        callback = None
        if create_encoder_callback is not None:
            callback = create_encoder_callback(encoder)

        monitor = MultipartEncoderMonitor(encoder, callback)

        result = requests.post(
            url=self.compose_url(url),
            data=monitor,
            headers={'Content-Type': monitor.content_type}
        )

        return self.postprocess_response(result)

    @staticmethod
    def postprocess_response(response):
        """

            Args:
                response (requests.Response):

            Returns:

            """
        json = RemoteConnection._to_json(response)
        try:
            response.raise_for_status()
            return json
        except requests.HTTPError as err:
            raise HSApiError("Error response from server", json)

    @staticmethod
    def _to_json(result):
        """
        Tries to parse json from response
        :param result: response
        :return: json dict
        """
        try:
            json_result = result.json()
            return json_result
        except JSONDecodeError:
            raise ResponseIsNotJson(result)
        except Exception as ex:
            raise HSApiError(ex)
