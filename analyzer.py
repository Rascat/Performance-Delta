import argparse
import glob
import json
import os
import statistics
from typing import Any, Dict, List

import const
import logger
import utils
from objects import (BenchmarkStatistics, CommitReport, CommitStatistics,
                     JUnitReport, build_commit_report)

DELTA_THRESHOLD = 2  # seconds
SPEEDUP_THRESHOLD = 2.0


def analyze(path_to_log_dir: str) -> None:
    """Reads data from test runs, computes benchmarking statistics and logs result."""
    filenames = get_log_file_names(path_to_log_dir)

    if len(filenames) is 0:
        print("Error: No log files found in %s" % path_to_log_dir)

    statistics_list = []
    for filename in filenames:
        with open(filename) as file:
            report_data_list = json.load(file)
            commit_report_list = list(
                map(build_commit_report, report_data_list))
            statistics = analyze_report_list(commit_report_list)
            statistics_list.append(statistics)
            logger.log_statistics(statistics, dest_dir=path_to_log_dir)

    salient_commits = find_salient_commits(statistics_list)
    logger.log_salient_commits(salient_commits, dest_dir=path_to_log_dir)


def find_salient_commits(
        benchmark_statistics_list: List[BenchmarkStatistics]) -> Dict[str, List[str]]:
    """From a list of commit statistics, return a dict where a revision id points to list of statistics that are salient."""
    result = {}  # type: Dict[str, List[str]]
    for benchmark_statistics in benchmark_statistics_list:
        test_name = benchmark_statistics.test_name
        commit_statistics_list = benchmark_statistics.commits

        for commit_statistics in commit_statistics_list:
            if is_salient(commit_statistics):
                rev_id = commit_statistics.hexsha
                data = utils.unpack(commit_statistics)
                data[const.TEST_NAME] = test_name
                data.pop(const.HEXSHA, None)

                if rev_id in result:
                    result[rev_id].append(data)
                else:
                    result[rev_id] = [data]

    return result


def is_salient(commit_statistics: CommitStatistics) -> bool:
    """Retruns a boolean indication whether a commit statistics object is salient or not."""
    return (commit_statistics.runtime_delta > DELTA_THRESHOLD
            or commit_statistics.speedup > SPEEDUP_THRESHOLD)


def get_log_file_names(path_to_log_dir: str) -> List[str]:
    """Returns a list of all JSON files in the specified dir."""
    filenames = utils.get_filenames_by_type(path_to_log_dir, 'json')
    return filenames


def analyze_report_list(reports: List[CommitReport]) -> BenchmarkStatistics:
    """Computes benchmark statistics from a list of test data.

    Returns a dict containing the statistics belonging to a test suite over a list of commits.
    """
    list_length = len(reports)
    std_dev = 0.0
    if list_length >= 2:
        std_dev = compute_std_deviation(reports)

    commit_statistics_list = []

    # compare perf of commit X with performance of following commit X+1 (an
    # earlier version)
    for i in range(list_length - 1):
        current_commit = reports[i].commit
        current_runtime = reports[i].report.time_elapsed
        next_runtime = reports[i + 1].report.time_elapsed

        runtime_delta = current_runtime - next_runtime
        speedup = current_runtime / \
            next_runtime if int(next_runtime) is not 0 else 0

        commit_statistics = CommitStatistics(
            hexsha=current_commit,
            runtime=current_runtime,
            speedup=speedup,
            runtime_delta=runtime_delta)

        commit_statistics_list.append(commit_statistics)

    test_name = reports[0].report.test_name
    benchmark_statistics = BenchmarkStatistics(
        test_name=test_name,
        std_dev=std_dev,
        delta_threshold=DELTA_THRESHOLD,
        speedup_threshold=SPEEDUP_THRESHOLD,
        commits=commit_statistics_list)

    return benchmark_statistics


def compute_std_deviation(reports: List[CommitReport]) -> float:
    """Returns the std deviation over all test execution times in list of test data objects.

    List must contain at least two data points.
    """
    runtimes = [report.report.time_elapsed for report in reports]
    return statistics.stdev(runtimes)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Analyze reports')
    parser.add_argument('directory', type=str,
                        help='Path to a directory where analyzable reports reside')
    parser.add_argument('--delta-threshold', type=str,
                        help='Set threshold to which the delta of the current commit compared to the next older one is tolerable')
    parser.add_argument('--speedup-threshold', type=str,
                        help='Set threshold to which the relation of the current runtime to the former one is tolerable')

    args = parser.parse_args()
    if args.delta_threshold is not None:
        DELTA_THRESHOLD = args.delta_threshold
    if args.speedup_threshold is not None:
        SPEEDUP_THRESHOLD = args.speedup_threshold

    analyze(args.directory)
