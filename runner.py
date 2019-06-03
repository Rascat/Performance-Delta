import constants
import parser
import glob
import utils
import os.path
import subprocess
import sys
import json
from pathlib import Path
from typing import List, Dict

from git import Repo # type: ignore

def run(path_to_repo: str, commit_count: int):
    repo = Repo(path_to_repo)
    path_to_pom = os.path.join(path_to_repo, constants.POM)
    
    commit_list = list(repo.iter_commits('master')) # list of all commits in branch master
    commit_list = commit_list[0 : commit_count] # get last n commits, counting from HEAD

    path_to_log = create_log_dir(path_to_repo)

    log_list = [] # type: List[Dict]

    for commit in commit_list:
        repo.git.checkout(commit.hexsha)
        run_mvn_test(path_to_pom)
        reports = collect_surefire_reports(path_to_repo)
        for report in reports:
            report_data = parser.parse_report(report)
            log_data = {"commit": commit.hexsha, "report": report_data}
            log_list.append(log_data)
    
    for grouped_list in group_logs_by_test_name(log_list):
        write_log_list(grouped_list, path_to_log)
    
    # checkout master again
    repo.git.checkout("master")


def create_log_dir(project_root: str) -> str:
    path = utils.get_log_dir(project_root)

    if not os.path.isdir(path):
        try:
            os.mkdir(path)
        except OSError:
            print("Creation of the directory %s failed" % path)
        else:
            print("Successfully created the directory %s" % path)
    
    return path


def run_mvn_test(path_to_pom: str):
    subprocess.run(["mvn clean test -f " + path_to_pom], shell = True)


def collect_surefire_reports(project_root: str) -> List[str]:
    path_to_reports = os.path.join(project_root, constants.MVN_TARGET_DIR, constants.SUREFIRE_REPORTS_DIR)
    return utils.get_filenames_by_type(path_to_reports, "txt")


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