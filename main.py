import argparse
import os
import sys
from typing import List

import analyzer
import runner
import utils


def csv_list(string: str) -> List[str]:
    return string.split(',')


def main():
    parser = argparse.ArgumentParser(description="Run tests from commit X to commit Y.")
    parser.add_argument('start', type=str, help="hash of commit to start from")
    parser.add_argument('end', type=str, help="hash of commit to go to, including")
    parser.add_argument('-p', '--path', type=str, help="path to maven project, defaults to the current working directory.")
    parser.add_argument('-d', '--destination', type=str, help="path to directory where resulting artifacts will be safed. Defaults to parent directory of project root.")
    parser.add_argument('-c', '--test-classes', type=csv_list, help='comma separated list of test classes to be run.')

    args = parser.parse_args()

    if args.path is None:
        project_root = os.getcwd()
    else:
        project_root = args.path
    
    if args.destination is None:
        log_dir = utils.get_default_log_dir(project_root)
    else:
        log_dir = args.destination

    test_classes = args.test_classes

    commit_from = args.start
    commit_to = args.end

    runner.run(path_to_repo=project_root, path_to_log=log_dir, start_commit=commit_from, end_commit=commit_to, test_classes=test_classes)
    analyzer.analyze(log_dir)


if __name__ == "__main__": main()
