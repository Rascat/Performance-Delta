import glob
import os.path
import subprocess
import sys
import json
from pathlib import Path
from typing import List, Dict

from git import Repo

home = str(Path.home())
# project_root = home + "/Code/peassquickstart"
# path_to_pom = project_root + "/pom.xml"

def main():
    if len(sys.argv) < 3:
        print("Please provide path to mvn repository and number of commits")
        exit(1)
    
    project_root = sys.argv[1]
    path_to_pom = project_root + "/pom.xml"
    commit_count = int(sys.argv[2])

    repo = Repo(project_root)
    if repo.is_dirty():
        print(repo.untracked_files)
    
    commit_list = list(repo.iter_commits('master')) # list of all commits in branch master
    commit_list = commit_list[0 : commit_count]

    path_to_log = create_log_dir(project_root)

    for commit in commit_list:
        repo.git.checkout(commit.hexsha)
        run_mvn_test(path_to_pom)
        reports = collect_surefire_reports(project_root)
        for report in reports:
            report_data = parse_report(report)
            log_data = {"commit": commit.hexsha, "report": report_data}
            filename = write_log(log_data, path_to_log)
    
    # checkout master again
    repo.git.checkout("master")


def run_mvn_test(path_to_pom: str):
    subprocess.run(["mvn clean test -f " + path_to_pom], shell = True)


def collect_surefire_reports(project_root: str) -> List[str]:
    path_to_reports = project_root + "/target/surefire-reports"
    return glob.glob(path_to_reports + "/*.txt") # glob.glob() returns list of txt files


def get_parent_dir(dir: str) -> str:
    return os.path.abspath(os.path.join(dir, os.pardir))


def create_log_dir(project_root: str) -> str:
    parent_dir = get_parent_dir(project_root)
    path = parent_dir + "/perfomance-delta"

    if not os.path.isdir(path):
        try:
            os.mkdir(path)
        except OSError:
            print("Creation of the directory %s failed" % path)
        else:
            print("Successfully created the directory %s" % path)
    
    return path

# Assumes surefire report is formatted as follows:
#
# -------------------------------------------------------------------------------
# Test set: org.rascat.TermsOfSumTest
# -------------------------------------------------------------------------------
# Tests run: 1, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.049 s - in org.rascat.TermsOfSumTest
def parse_report(path_to_report: str) -> Dict:
    line_list = [line.rstrip('\n') for line in open(path_to_report)]
    line_test_info = line_list[3]
    line_test_info = line_test_info.strip()
    test_data = line_test_info.split(' ')

    tests_run = int(test_data[2].rstrip(','))
    failures = int(test_data[4].rstrip(','))
    errors = int(test_data[6].rstrip(','))
    skipped = int(test_data[8].rstrip(','))
    time_elapsed = float(test_data[11].rstrip(','))
    test_name = test_data[15]

    return {
        "test_run": tests_run,
        "failures": failures,
        "errors": errors,
        "skipped": skipped,
        "time_elapsed": time_elapsed,
        "test_name": test_name
        }


def write_log(data: Dict, path_to_log: str) -> str:
    filename = data["report"]["test_name"] + ".json"
    path = os.path.join(path_to_log, filename)

    if os.path.exists(path):
        append_write = 'a'
    else:
        append_write = 'w'

    with open(path, append_write) as file:
        file.write(json.dumps(data, indent=2))
    
    return path


def read_log(path: str):
    print(json.loads(path))
    

def split_list(list_of_dicts: List[Dict], key: str):
    pass

# argv[1]: path to maven project
# argv[2]: number of commits to iterate, starting from HEAD
if __name__ == "__main__": main()
