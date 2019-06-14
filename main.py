import argparse
import sys
import os

import analyzer
import runner
import utils


def main():
    parser = argparse.ArgumentParser(description="Run tests from commit X to commit Y.")
    parser.add_argument('start', type=str, help="hash of commit to start from")
    parser.add_argument('end', type=str, help="hash of commit to go to, including")
    parser.add_argument('-p', '--path', type=str, help="path to maven project, defaults to the current working directory.")
    parser.add_argument('-d', '--destination', type=str, help="path to directory where resulting artifacts will be safed. Defaults to parent directory of project root.")

    args = parser.parse_args()
    
    if args.path is None:
        project_root = os.getcwd()
    else:
        project_root = args.path
    
    if args.destination is None:
        log_dir = utils.get_default_log_dir(project_root)
    else:
        log_dir = args.destination

    commit_from = args.start
    commit_to = args.end

    runner.run(project_root, log_dir, commit_from, commit_to)
    analyzer.analyze(log_dir)


# argv[1]: path to maven project
# argv[2]: hash of commit where to start test exection
# argv[3]: hash of commit where to end test execution
if __name__ == "__main__": main()
