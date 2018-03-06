import json
import urllib.request
from json import JSONDecodeError

import requests

from hydroserving.httpclient.errors import *


class RemoteConnection:
    def __init__(self, remote_addr):
        self.remote_addr = remote_addr

    @staticmethod
    def send_request(request):
        """
        Sends a request
        :param request: urllib.request.Request
        :return: json dict
        """
        if not isinstance(request, urllib.request.Request):
            raise RuntimeError("{} is not a urllib.request.Request".format(request))

        f = urllib.request.urlopen(request)
        resp_body = f.read().decode("utf-8")
        try:
            response = json.loads(resp_body)
            return response
        except JSONDecodeError:
            raise ResponseIsNotJson(request)
        except Exception as ex:
            raise HSApiError(ex)
        finally:
            f.close()

    def compose_url(self, url):
        return self.remote_addr + url

    def post(self, url, data):
        """
        Sends POST request with `data` to the given `url` and returns data as JSON dictionary.
        """
        json_data = json.dumps(data)
        request = urllib.request.Request(
            self.compose_url(url),
            json_data.encode('utf-8'),
            {'Content-Type': 'application/json'}
        )
        return RemoteConnection.send_request(request)

    def get(self, url):
        """
        Sends GET request with to the given `url` and returns data as JSON dictionary.
        """
        req = urllib.request.Request(self.compose_url(url))
        return RemoteConnection.send_request(req)

    def multipart_post(self, url, data, files):
        try:
            result = requests.post(
                self.compose_url(url),
                data=data,
                files=files
            )
            return result.text
        except JSONDecodeError as ex:
            raise ResponseIsNotJson(ex)
        except Exception as ex:
            raise HSApiError(ex)
