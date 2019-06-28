import glob
import json
import os
import statistics
from typing import Dict, List, Any

import const
import logger
import utils

STD_DEV_THRESHOLD = 0.2
DELTA_THRESHOLD = 0.2
SPEEDUP_THRESHOLD = 1.0
STAT_DIR = "statistics"

def analyze(path_to_log_dir: str):
    """Reads data from test runs, computes benchmarking statistics and logs result."""
    filenames = get_log_file_names(path_to_log_dir)

    if len(filenames) is 0:
        print("Error: No log files found in %s" % path_to_log_dir)

    statistics_list = []
    for filename in filenames:
        with open(filename) as file:
            log_list = json.load(file)
            statistics = analyze_log_list(log_list)
            statistics_list.append(statistics)
            stat_dir_path = os.path.join(path_to_log_dir, STAT_DIR)
            logger.log_statistics(statistics, dest_dir = stat_dir_path)

    salient_commits = find_salient_commits(statistics_list)
    logger.log_salient_commits(salient_commits)
    
            

def get_log_file_names(path_to_log_dir: str) -> List[str]:
    """Returns a list of all JSON files in the specified dir."""
    filenames = utils.get_filenames_by_type(path_to_log_dir, 'json')
    return filenames


def analyze_log_list(log_list: List[Dict[str, Any]]) -> Dict:
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
    analysis_result[const.STD_DEVIATION_THRESHOLD] = STD_DEV_THRESHOLD
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

def find_salient_commits(statistics_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyzes a given statistics dict and returns a summary of commits which changed the performance more than expected.
    
    Things that qualify as 'unexpected change in performance':
    |(current runtime - former-runtime)| > delta-threshold
    (current-runtime / former-runtime) > speedup-threshold
    """
    salient_commits = {}
    salient_commits[const.TEST_NAME] = statistics_list[const.TEST_NAME]

    commits = []
    for commit in statistics_list[const.COMMITS]:
        if abs(commit[const.RUNTIME_DELTA]) > statistics_list[const.DELTA_THRESHOLD]:
            commits.append(commit)
        
        if commit[const.SPEEDUP] > statistics_list[const.SPEEDUP_THRESHOLD]:
            commits.append(commit)
    
    salient_commits[const.COMMITS] = commits
    return salient_commits
