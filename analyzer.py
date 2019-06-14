import glob
import json
import os
import statistics
from typing import Dict, List

import constants
import logger
import utils

STD_DEV_THRESHOLD = 0.2
DELTA_THRESHOLD = 0.2
STAT_DIR = "statistics"

def analyze(path_to_log_dir: str):
    """Reads data from test runs, computes benchmarking statistics and logs result."""
    filenames = get_log_file_names(path_to_log_dir)

    if len(filenames) is 0:
        print("Error: No log files found in %s" % path_to_log_dir)

    for filename in filenames:
        with open(filename) as file:
            log_list = json.load(file)
            statistics = analyze_log_list(log_list)
            stat_dir_path = os.path.join(path_to_log_dir, STAT_DIR)
            logger.log(statistics, dest_dir = stat_dir_path)
            

def get_log_file_names(path_to_log_dir: str) -> List[str]:
    """Returns a list of all JSON files in the specified dir."""
    filenames = utils.get_filenames_by_type(path_to_log_dir, 'json')
    return filenames


def analyze_log_list(log_list: List[Dict]) -> Dict:
    """Computes benchmark statistics from a list of test data.
    
    Returns a dict containing the statistics belonging to a test suite over a list of commits.
    """

    list_length = len(log_list)
    std_dev = 0.0
    if list_length >= 2:
        std_dev = compute_std_deviation(log_list)

    analysis_result = {}
    analysis_result['test_name'] = log_list[0].get(constants.REPORT).get(constants.TEST_NAME)
    analysis_result['std_dev'] = std_dev
    analysis_result['delta_threshold'] = DELTA_THRESHOLD
    analysis_result['std_dev_threshold'] = STD_DEV_THRESHOLD
    analysis_result['commits'] = []

    # compare perf of commit X with performance of following commit X+1 (an earlier version)
    for i in range(list_length - 1):
        current_commit = log_list[i][constants.COMMIT]
        current_runtime = log_list[i][constants.REPORT][constants.TIME_ELAPSED]
        next_runtime = log_list[i + 1][constants.REPORT][constants.TIME_ELAPSED]

        runtime_delta = current_runtime - next_runtime
        speedup = current_runtime / next_runtime if int(next_runtime) is not 0 else 0

        commit_statistics = {}
        commit_statistics['hexsha'] = current_commit
        commit_statistics['runtime'] = current_runtime
        commit_statistics['speedup'] = speedup
        commit_statistics['runtime_delta'] = runtime_delta

        analysis_result['commits'].append(commit_statistics)

    return  analysis_result


def compute_std_deviation(log_list: List[Dict]) -> float:
    """Returns the std deviation over all test execution times in list of test data objects.
    
    List must contain at least two data points.
    """
    runtimes = [log[constants.REPORT][constants.TIME_ELAPSED] for log in log_list]
    return statistics.stdev(runtimes)
