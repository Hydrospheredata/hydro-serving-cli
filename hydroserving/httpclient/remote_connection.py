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
        data = self.preprocess_request(data)
        print(data)
        result = requests.post(self.compose_url(url), json=data)
        return self.postprocess_response(result)

    def put(self, url, data):
        """
        Sends PUT request with `data` to the given `url` and returns data as JSON dictionary.
        """
        data = self.preprocess_request(data)
        print(data)
        result = requests.put(self.compose_url(url), json=data)
        return self.postprocess_response(result)

    def get(self, url):
        """
        Sends GET request with to the given `url` and returns data as JSON dictionary.
        """
        result = requests.get(self.compose_url(url))
        return self.postprocess_response(result)

    def delete(self, url):
        """
        Sends DELETE request with to the given `url` and returns data as JSON dictionary.
        """
        result = requests.delete(self.compose_url(url))
        return self.postprocess_response(result)

    def multipart_post(self, url, data, files, create_encoder_callback=None):
        encoder = MultipartEncoder(
            fields={**self.preprocess_request(data), **files}
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
    def preprocess_request(request):
        return RemoteConnection._remove_none(request)

    @staticmethod
    def postprocess_response(response):
        """

            Args:
                response (requests.Response):

            Returns:

            """
        try:
            response.raise_for_status()
            json = RemoteConnection._to_json(response)
            return json
        except requests.HTTPError as err:
            raise HSApiError("Error response from server", response.text)

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

    @staticmethod
    def _remove_none(obj):
        if isinstance(obj, (list, tuple, set)):
            return type(obj)(RemoteConnection._remove_none(x) for x in obj if x is not None)
        elif isinstance(obj, dict):
            return dict((RemoteConnection._remove_none(k), RemoteConnection._remove_none(v))
                        for k, v in obj.items() if k is not None and v is not None)
        elif hasattr(obj, '__dict__'):
            return RemoteConnection._remove_none(obj.__dict__)
        else:
            return obj
