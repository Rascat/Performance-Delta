import os
from os import path
from typing import Any, Dict, List

from tabulate import tabulate

import const
import utils
from model.objects import BenchmarkStatistics, JmhStatistics


def log_benchmark_statistics(statistics: BenchmarkStatistics, dest_dir: str = None) -> None:
    """Logs data contained by dict to the specified directory.

    The filename of a given statistics dict is equal to the test name.
    If no path to a destination directory is provided, the data is printed to std out.
    """
    statistics_str = format_benchmark_statistics(statistics)
    if dest_dir is None:
        print(statistics_str)
    else:
        stat_dir = os.path.join(dest_dir, const.STATISTICS_DIR)
        utils.create_dir(stat_dir)
        destination = path.join(stat_dir, statistics.test_name)
        with open(destination, "w") as file:
            file.write(statistics_str)


def log_jmh_statistics(statistics: List[JmhStatistics], dest_dir: str = None) -> None:
    if dest_dir is None:
        print(utils.unpack(statistics))


def log_salient_commits(
        salient_commits: Dict[str, List[Any]], dest_dir: str = None) -> None:
    salient_commits_str = format_salient_commits(salient_commits)
    if dest_dir is None:
        print(salient_commits_str)
    else:
        stat_dir = os.path.join(dest_dir, const.STATISTICS_DIR)
        filename = path.join(stat_dir, 'salient_commits.txt')
        with open(filename, 'w') as file:
            file.write(salient_commits_str)


def format_benchmark_statistics(statistics: BenchmarkStatistics) -> str:
    """Formats a given test statistics dict and returns a string representation"""
    header = ("{s.test_name}\n\n"
              "Std deviation: {s.std_dev}\n"
              "Delta threshold: {s.delta_threshold}\n"
              "Speedup threshold: {s.speedup_threshold}\n\n").format(s=statistics)

    records = tabulate(utils.unpack(statistics.junit_statistics), headers="keys")

    return header + records


def format_salient_commits(salient_commits: Dict[str, List[Any]]) -> str:
    header = ('The following commits introduced changes that extended '
              'the runtime of some test classes on branch {branch}.\n\n').format(branch='master')
    body = ''
    for key in salient_commits.keys():
        body += '{hexsha}:\n\n'.format(hexsha=key)
        body += tabulate(salient_commits[key], headers='keys')
        body += '\n\n'

    return header + body
