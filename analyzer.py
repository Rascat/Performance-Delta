import glob
import json
import os
import statistics
from typing import Dict, List, Any

import const
import logger
import utils

DELTA_THRESHOLD = 2 # seconds
SPEEDUP_THRESHOLD = 1.0


def analyze(path_to_log_dir: str) -> None:
    """Reads data from test runs, computes benchmarking statistics and logs result."""
    filenames = get_log_file_names(path_to_log_dir)

    if len(filenames) is 0:
        print("Error: No log files found in %s" % path_to_log_dir)

    statistics_list = []
    for filename in filenames:
        with open(filename) as file:
            report_list = json.load(file)
            statistics = analyze_report_list(report_list)
            statistics_list.append(statistics)
            logger.log_statistics(statistics, dest_dir = path_to_log_dir)
    
    salient_commits = find_salient_commits(statistics_list)
    logger.log_salient_commits(salient_commits, dest_dir=path_to_log_dir)

    
def find_salient_commits(statistics_list: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    result = {} # type: Dict[str, List[str]]
    for statistics in statistics_list:
        test_name = statistics[const.TEST_NAME]
        commits = statistics[const.COMMITS]

        for commit in commits:
            if is_salient(commit):
                rev_id = commit[const.HEXSHA]
                data = commit
                data[const.TEST_NAME] = test_name
                data.pop(const.HEXSHA, None)

                if rev_id in result:
                    result[rev_id].append(data)
                else:
                    result[rev_id] = [data]

    return result


def is_salient(commit_statistics: Dict[str, Any]) -> bool:
    return (commit_statistics[const.RUNTIME_DELTA] > DELTA_THRESHOLD
        or commit_statistics[const.SPEEDUP] > SPEEDUP_THRESHOLD)


def get_log_file_names(path_to_log_dir: str) -> List[str]:
    """Returns a list of all JSON files in the specified dir."""
    filenames = utils.get_filenames_by_type(path_to_log_dir, 'json')
    return filenames


def analyze_report_list(log_list: List[Dict[str, Any]]) -> Dict:
    """Computes benchmark statistics from a list of test data.
    
    Returns a dict containing the statistics belonging to a test suite over a list of commits.
    """
    list_length = len(log_list)
    std_dev = 0.0
    if list_length >= 2:
        std_dev = compute_std_deviation(log_list)

    analysis_result = {}
    analysis_result[const.TEST_NAME] = log_list[0].get(const.REPORT).get(const.TEST_NAME)
    analysis_result[const.STD_DEVIATION] = std_dev
    analysis_result[const.DELTA_THRESHOLD] = DELTA_THRESHOLD
    analysis_result[const.SPEEDUP_THRESHOLD] = SPEEDUP_THRESHOLD
    analysis_result[const.COMMITS] = []

    # compare perf of commit X with performance of following commit X+1 (an earlier version)
    for i in range(list_length - 1):
        current_commit = log_list[i][const.COMMIT]
        current_runtime = log_list[i][const.REPORT][const.TIME_ELAPSED]
        next_runtime = log_list[i + 1][const.REPORT][const.TIME_ELAPSED]

        runtime_delta = current_runtime - next_runtime
        speedup = current_runtime / next_runtime if int(next_runtime) is not 0 else 0

        commit_statistics = {}
        commit_statistics[const.HEXSHA] = current_commit
        commit_statistics[const.RUNTIME] = current_runtime
        commit_statistics[const.SPEEDUP] = speedup
        commit_statistics[const.RUNTIME_DELTA] = runtime_delta

        analysis_result[const.COMMITS].append(commit_statistics)

    return  analysis_result


def compute_std_deviation(log_list: List[Dict]) -> float:
    """Returns the std deviation over all test execution times in list of test data objects.
    
    List must contain at least two data points.
    """
    runtimes = [log[const.REPORT][const.TIME_ELAPSED] for log in log_list]
    return statistics.stdev(runtimes)
