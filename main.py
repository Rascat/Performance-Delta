import glob
import os.path
import subprocess
import sys
import json
from pathlib import Path
from typing import List, Dict

from git import Repo # type: ignore

def main():
    if len(sys.argv) < 3:
        print("Please provide path to mvn repository and number of commits")
        exit(1)
    
    project_root = sys.argv[1] # type: str
    path_to_pom = project_root + "/pom.xml" # type: str
    commit_count = int(sys.argv[2]) # type: int

    repo = Repo(project_root)
    
    commit_list = list(repo.iter_commits('master')) # list of all commits in branch master
    commit_list = commit_list[0 : commit_count] # get last n commits, counting from HEAD

    path_to_log = create_log_dir(project_root)

    log_list: List[Dict] = []

    for commit in commit_list:
        repo.git.checkout(commit.hexsha)
        run_mvn_test(path_to_pom)
        reports = collect_surefire_reports(project_root)
        for report in reports:
            report_data = parse_report(report)
            log_data = {"commit": commit.hexsha, "report": report_data}
            log_list.append(log_data)
    
    for grouped_list in group_logs_by_test_name(log_list):
        write_log_list(grouped_list, path_to_log)
    
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
    path = parent_dir + "/perfdelta-results"

    if not os.path.isdir(path):
        try:
            os.mkdir(path)
        except OSError:
            print("Creation of the directory %s failed" % path)
        else:
            print("Successfully created the directory %s" % path)
    
    return path

def parse_report(path_to_report: str) -> Dict:
    """
    Assumes surefire report is formatted as follows:

    -------------------------------------------------------------------------------
    Test set: org.rascat.TermsOfSumTest
    -------------------------------------------------------------------------------
    Tests run: 1, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.049 s - in org.rascat.TermsOfSumTest
    """
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


def group_logs_by_test_name(log_list: List) -> List[List[Dict]]:
    """
    Groups a list of dicts like [{'test_name': 'X'},{'test_name': 'Y'}, {'test_name': 'X'}]
    to a list of lists like [[{'test_name': 'X'}, {'test_name': 'X'}], [{'test_name': 'Y'}]]
    """
    grouped_log_list = [] # type: List[List[Dict]]
    test_result_map = {} # type: Dict[str, List]

    for log in log_list:
        test_name = log['report']['test_name']
        if test_name not in test_result_map.keys():
            test_result_map[test_name] = [log]
        else:
            test_result_map[test_name].append(log)
    
    for key in test_result_map.keys():
        grouped_log_list.append(test_result_map[key])
    
    return grouped_log_list


def write_log_list(log_list: List, path_to_log: str) -> str:
    filename = log_list[0]['report']['test_name'] + '.json'
    path = os.path.join(path_to_log, filename)

    with open(path, 'w') as file:
        file.write(json.dumps(log_list, indent=2))
    
    return filename


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
