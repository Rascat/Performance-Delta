import constants
import os.path
import glob
from typing import List

def get_parent_dir(child_dir: str) -> str:
    return os.path.abspath(os.path.join(child_dir, os.pardir))


def get_log_dir(path_to_repo: str) -> str:
    parent_dir = get_parent_dir(path_to_repo)
    return os.path.join(parent_dir, constants.RESULTS_DIRECTORY)


def get_filenames_by_type(path: str, filetype: str) -> List[str]:
    return glob.glob(path + os.path.sep + "*." + filetype)