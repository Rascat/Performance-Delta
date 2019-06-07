import analyzer
import argparse
import sys
import utils
import runner

def main():
    parser = argparse.ArgumentParser(description="Run tests from commit X to commit Y.")
    parser.add_argument('path', type=str, help="path to maven project")
    parser.add_argument('start', type=str, help="hexsha of commit to start from")
    parser.add_argument('end', type=str, help="hexsha of commit to go to, including")

    args = parser.parse_args()
    
    project_root = args.path
    commit_from = args.start
    commit_to = args.end

    # runner.run(project_root, commit_from, commit_to)
    log_dir = utils.get_log_dir(project_root)
    analyzer.analyze(log_dir)


# argv[1]: path to maven project
# argv[2]: number of commits to iterate, starting from HEAD
if __name__ == "__main__": main()
