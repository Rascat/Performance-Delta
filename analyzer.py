import glob
import constants
import utils
import os
import logger
import json
import statistics
from typing import List, Dict

STD_DEV_THRESHOLD = 0.2
DELTA_THRESHOLD = 0.2

def analyze(path_to_log_dir: str):
    filenames = get_log_file_names(path_to_log_dir)

    if len(filenames) is 0:
        print("Error: No log files found in %s" % path_to_log_dir)

    for filename in filenames:
        with open(filename) as file:
            log_list = json.load(file)
            analyze_log_list(log_list)
            

def get_log_file_names(path_to_log_dir: str) -> List[str]:
    filenames = utils.get_filenames_by_type(path_to_log_dir, 'json')
    return filenames


def analyze_log_list(log_list: List[Dict]):
    list_length = len(log_list)
    std_dev = compute_std_deviation(log_list)
    logger.print_info(log_list[0].get(constants.REPORT).get(constants.TEST_NAME), std_dev)

    # compare perf of commit X with performance of following commit X+1 (an earlier versions)
    logger.print_header()
    for i in range(list_length - 1):
        current_commit = log_list[i][constants.COMMIT]
        next_commit = log_list[i + 1][constants.COMMIT]
        current_runtime = log_list[i][constants.REPORT][constants.TIME_ELAPSED]
        next_runtime = log_list[i + 1][constants.REPORT][constants.TIME_ELAPSED]

        runtime_delta = current_runtime - next_runtime
        logger.log_delta(current_commit, current_runtime, runtime_delta, current_runtime / next_runtime)
        if (current_runtime * DELTA_THRESHOLD) > next_runtime:
            logger.warn(current_commit, next_commit, runtime_delta, DELTA_THRESHOLD)


def compute_std_deviation(log_list) -> float:
    runtimes = [log[constants.REPORT][constants.TIME_ELAPSED] for log in log_list]
    return statistics.stdev(runtimes)


