import glob
import os.path
from typing import List

import const


def get_parent_dir(child_dir: str) -> str:
    """Returns path to parent dir of the specified dir."""
    return os.path.abspath(os.path.join(child_dir, os.pardir))


def get_default_log_dir(path_to_repo: str) -> str:
    """Returns path to dir where test execution data and statistics are being written to."""
    parent_dir = get_parent_dir(path_to_repo)
    return os.path.join(parent_dir, const.RESULTS_DIRECTORY)


def get_filenames_by_type(path: str, filetype: str) -> List[str]:
    """Returns a list of filenames for files of the specified type in the given dir."""
    return glob.glob(path + os.path.sep + "*." + filetype)


def create_dir(path: str) -> str:
    """Creates the specified directory if it is not already present."""
    
    if not os.path.isdir(path):
        try:
            os.mkdir(path)
        except OSError:
            print("Creation of the directory %s failed" % path)
        else:
            print("Successfully created the directory %s" % path)
    
    return path
