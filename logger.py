import sys
import const
import os
from os import path
from typing import Dict, List, Any

import utils


def warn(current_commit: str, next_commit: str, delta: float, threshold: float):
    print("WARNING: {} introduced performance change. Delta: {}. Threshold: {}.".format(current_commit, delta, threshold), file=sys.stderr)


def log_statistics(statistics: Dict, dest_dir: str = None):
    """Logs data contained by dict to the specified directory.
    
    The filename of a given statistics dict is equal to the test name.
    If no path to a destination directory is provided, the data is printed to std out.
    """
    statistics_str = format_statistics(statistics)
    if dest_dir is None:
        print(statistics_str)
    else:
        stat_dir = os.path.join(dest_dir, const.STATISTICS_DIR)
        utils.create_dir(stat_dir)
        destination = path.join(stat_dir, statistics['test_name'])
        with open(destination, "w") as file:
            file.write(statistics_str)


def log_salient_commits(salient_commits: Dict[str, List[Any]], dest_dir: str = None) -> None:
    salient_commits_str = format_salient_commits(salient_commits)
    if dest_dir is None:
        print(salient_commits_str)
    else:
        stat_dir = os.path.join(dest_dir, const.STATISTICS_DIR)
        filename = path.join(stat_dir, 'salient_commits.txt')
        with open(filename, 'w') as file:
            file.write(salient_commits_str)


def format_statistics(statistics: Dict) -> str:
    """Formats a given test statistics dict and returns a string representation"""
    header = ("{s[test_name]}\n\n"
                "Std deviation: {s[std_dev]}\n"
                "Delta threshold: {s[delta_threshold]}\n"
                "Speedup threshold: {s[speedup_threshold]}\n\n").format(s=statistics)
    
    top_row = "{:<42}{:<9}{:<9}{:<5}\n".format('commit', 'runtime','delta', 'speedup')

    records = ""
    for commit_statistics in statistics['commits']:
        records += "{c[hexsha]:<42}{c[runtime]:<9.3f}{c[runtime_delta]:<9.3f}{c[speedup]:<5.3f}\n".format(c=commit_statistics)
    
    return header + top_row + records


def format_salient_commits(salient_commits: Dict[str, List[Any]]) -> str:
    header = "The following commits introduced changes that extended the runtime of some test classes.\n\n"
    body = ""
    for key in salient_commits.keys():
        body += "{hexsha}:".format(hexsha=key)
        for statistic in salient_commits[key]:
            body += "\n{s[test_name]} [{s[runtime_delta]:.4f}s] [{s[speedup]:.4f}]".format(s=statistic)
        body += "\n\n"
    
    return header + body

