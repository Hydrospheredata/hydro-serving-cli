import logging 

from hydrosdk.exceptions import BadRequestException, BadResponseException
from requests.exceptions import ConnectTimeout, ConnectionError 


def handle_cluster_error(func):
    def inner(*args, **kwargs):
        try: 
            return func(*args, **kwargs)
        except (BadRequestException, BadResponseException) as e:
            logging.error(e)
            raise SystemExit(-1)
        except (ConnectionError, ConnectTimeout) as e:
            logging.error(f"Failed to connect to the cluster due to: {e}", stack_info=e.strerror)
            raise SystemExit(-1)
    return inner