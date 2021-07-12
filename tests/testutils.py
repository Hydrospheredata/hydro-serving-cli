from io import BytesIO
import shutil
import os

import requests

from hs.settings import TARGET_FOLDER

def mock_sse_response(data: bytes):
    resp = requests.Response()
    resp.status_code = 200
    resp.headers["Content-Type"] = "text/event-stream"
    resp.raw = BytesIO(data)
    return resp

def with_cwd(new_cwd, func, *args):
    """
    Wrapper util to run some function in new Current Working Directory
    :param new_cwd: path to the new CWD
    :param func: callback
    :param args: args to the `func`
    :return: result of `func`
    """
    old_cwd = os.getcwd()
    try:
        os.chdir(new_cwd)
        result = func(*args)
        return result
    except Exception as err:
        raise err
    finally:
        os.chdir(old_cwd)

def with_target_cwd(cwd, func, *args):
    """
    Wrapper util to run some function in new Current Working Directory.
    Removes TARGET_PATH directory after execution
    :param cwd: path to the new CWD
    :param func: callback
    :param args: args to the `func`
    :return: result of `func`
    """
    target_path = os.path.join(cwd, TARGET_FOLDER)
    try:
        with_cwd(cwd, func, *args)
    except Exception as ex:
        raise ex
    finally:
        if os.path.exists(target_path):
            shutil.rmtree(target_path)
