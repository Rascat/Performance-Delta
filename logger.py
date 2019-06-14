import sys
from os import path
from typing import Dict

import utils


def warn(current_commit: str, next_commit: str, delta: float, threshold: float):
    print("WARNING: {} introduced performance change. Delta: {}. Threshold: {}.".format(current_commit, delta, threshold), file=sys.stderr)


def log(statistics: Dict, dest_dir: str = None):
    """Logs data contained by dict to the specified directory.
    
    The filename of a given statistics dict is equal to the test name.
    If no path to a destination directory is provided, the data is printed to std out.
    """
    statistics_str = format_statistics(statistics)
    if dest_dir is None:
        print(statistics_str)
    else:
        utils.create_dir(dest_dir)
        destination = path.join(dest_dir, statistics['test_name'])
        with open(destination, "w") as file:
            file.write(statistics_str)


def format_statistics(statistics: Dict) -> str:
    """Formats a given test statistics dict and returns a string representation"""
    header = ("{s[test_name]}\n\n"
                "Std deviation: {s[std_dev]}\n"
                "Delta threshold: {s[delta_threshold]}\n"
                "Std deviation threshold: {s[std_dev_threshold]}\n\n").format(s=statistics)
    
    top_row = "{:<42}{:<9}{:<9}{:<5}\n".format('commit', 'runtime','delta', 'speedup')

    records = ""
    for commit_statistics in statistics['commits']:
        records += "{c[hexsha]:<42}{c[runtime]:<9.3f}{c[runtime_delta]:<9.3f}{c[speedup]:<5.3f}\n".format(c=commit_statistics)
    
    return header + top_row + records
