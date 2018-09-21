import shutil
import os

from hydroserving.constants.package import TARGET_FOLDER
from hydroserving.helpers.package import with_cwd


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
