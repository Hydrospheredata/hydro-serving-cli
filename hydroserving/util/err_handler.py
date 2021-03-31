import logging 

from hydrosdk.exceptions import BadRequestException, BadResponseException, TimeoutException
from requests.exceptions import ConnectTimeout, ConnectionError 


def handle_cluster_error(func):
    def inner(*args, **kwargs):
        if hasattr(args[0], 'cluster') and args[0].cluster is None:
            logging.error("Current cluster is unset, use 'hs cluster set [NAME]' to set an active cluster")
            raise SystemExit(1)
        try: 
            return func(*args, **kwargs)
        except (BadRequestException, BadResponseException, TimeoutException) as e:
            logging.error(e)
            raise SystemExit(1)
        except (ConnectionError, ConnectTimeout) as e:
            logging.error(f"Failed to connect to the cluster due to: {e}", stack_info=e.strerror)
            raise SystemExit(1)
    return inner