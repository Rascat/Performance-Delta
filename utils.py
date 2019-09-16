import glob
import os.path
from typing import List, Dict, Any

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
            print('Creation of the directory {dir} failed'.format(dir=path))
            exit(1)
        else:
            print('Successfully created the directory {dir}'.format(dir=path))

    return path


def is_named_tuple(x):
    """Copy pasted from stack overflow

    https://stackoverflow.com/questions/33181170/how-to-convert-a-nested-namedtuple-to-a-dict
    """
    _type = type(x)
    bases = _type.__bases__
    if len(bases) != 1 or bases[0] != tuple:
        return False
    fields = getattr(_type, '_fields', None)
    if not isinstance(fields, tuple):
        return False
    return all(isinstance(i, str) for i in fields)


def unpack(obj):
    """Copy pasted from stack overflow

    https://stackoverflow.com/questions/33181170/how-to-convert-a-nested-namedtuple-to-a-dict
    """
    if isinstance(obj, dict):
        return {key: unpack(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [unpack(value) for value in obj]
    elif is_named_tuple(obj):
        return {key: unpack(value) for key, value in obj._asdict().items()}
    elif isinstance(obj, tuple):
        return tuple(unpack(value) for value in obj)
    else:
        return obj


def compute_speedup(gradoop_benchmark_report: List[Dict[str, Any]]) -> None:
    mean_runtime_p1 = 'undefined'

    for row in gradoop_benchmark_report:
        if row['parallelism'] is 1:
            mean_runtime_p1 = row['mean_runtime']
            break

    speedup_list = []
    for row in gradoop_benchmark_report:
        if row['parallelism'] > 1:
            key = 'speedup_p' + str(row['parallelism'])
            value = mean_runtime_p1 / row['mean_runtime']
            speedup = {key: value}
            speedup_list.append(speedup)
