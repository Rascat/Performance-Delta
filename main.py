import argparse
import os
import sys
from typing import List

import analyzer
import runner
import utils


def main():
    parser = argparse.ArgumentParser(
        description="Run tests over a range of commits.")
    parser.add_argument('-i', '--interval', type=str, nargs=2, metavar=('start', 'end'),
                        help="specify an interval of commits, starting with the recent one.")
    parser.add_argument('-s', '--selection', type=str, nargs='*',
                        metavar='commit-id', help='a number of commits ids in decreasing recency.')
    parser.add_argument('-p', '--path', type=str,
                        help="path to maven project, defaults to the current working directory.")
    parser.add_argument('-d', '--destination', type=str,
                        help="path to directory where resulting artifacts will be saved. Defaults to parent directory of project root.")
    parser.add_argument('-c', '--test-classes', type=str,
                        nargs='*', help='list of test classes to be run.')
    parser.add_argument('-b', '--branch', type=str, default="master",
                        help='name of the branch to test (defaults to "master").')
    parser.add_argument('--invocation-count', type=int, metavar='count',
                        help='the number of times each test should be invoked. Logging happens after the last run.', default=1)

    args = parser.parse_args()

    interval = args.interval
    selection = args.selection
    if interval is None and selection is None:
        print("Please specify either an interval or a selection of commit ids.")
        exit(1)
    if interval is not None and selection is not None:
        print('Please provide only an interval or a selection of commits ids, not both.')
        exit(1)

    commit_ids = interval if interval is not None else selection
    is_interval = True if interval is not None else False

    if args.path is None:
        project_root = os.getcwd()
    else:
        project_root = args.path

    if args.destination is None:
        log_dir = utils.get_default_log_dir(project_root)
    else:
        log_dir = args.destination

    test_classes = args.test_classes
    branch = args.branch
    invocation_count = args.invocation_count

    runner.run(path_to_repo=project_root, path_to_log=log_dir, commit_ids=commit_ids,
               is_interval=is_interval, test_classes=test_classes, branch=branch, invocation_count=invocation_count)
    analyzer.analyze(log_dir)


# argv[1]: path to maven project
# argv[2]: hash of commit where to start test execution
# argv[3]: hash of commit where to end test execution
if __name__ == "__main__":
    main()
