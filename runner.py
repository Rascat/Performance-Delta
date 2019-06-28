import glob
import json
import os.path
import parser
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any

from git import Repo  # type: ignore

import const
import utils


def run(path_to_repo: str, path_to_log: str, start_commit: str, end_commit: str, test_classes: List[str] = None):
    """Runs a maven repositories test suite over a range of commits and logs commit specific execution times."""
    repo = Repo(path_to_repo)
    path_to_parent_pom = os.path.join(path_to_repo, const.POM)
    
    commit_list = list(repo.iter_commits('master')) # list of all commits in branch master

    index_start = commit_list.index(repo.commit(start_commit))
    index_end = commit_list.index(repo.commit(end_commit))

    if (index_start >= index_end):
        print("Error, wrong commit order. First commit must be younger than the second one.")
        exit(1)

    commit_list = commit_list[index_start: index_end + 1] # get last n commits, counting from HEAD

    utils.create_dir(path_to_log)

    log_list = [] # type: List[Dict]

    for commit in commit_list:
        repo.git.checkout(commit.hexsha)
        if test_classes is None:
            run_mvn_test(path_to_parent_pom)
        else:
            run_mvn_test_selected(path_to_parent_pom, test_classes)

        submodules = filter_target_modules(collect_submodules(path_to_parent_pom))

        for submodule in submodules:
            reports = collect_surefire_reports(submodule)
            for report in reports:
                report_data = parser.parse_report(report)
                log_data = {"commit": commit.hexsha, "report": report_data}
                log_list.append(log_data)
    
    for grouped_list in group_logs_by_test_name(log_list):
        write_log_list(grouped_list, path_to_log)
    
    # checkout master again
    repo.git.checkout("master")


def run_mvn_test(path_to_parent_pom: str):
    """Triggers test execution with surefire for the maven project specified in the pom."""
    subprocess.run(["mvn clean test -f " + path_to_parent_pom], shell=True)


def run_mvn_test_selected(path_to_parent_pom: str, test_classes: List[str]):
    """Triggers test execution with surefire for a selection of test classes"""
    comma_separated_classes = ",".join(test_classes)
    cmd = "mvn clean test -DfailIfNoTests=false -Dtest={classes} -am -f {pom}".format(pom=path_to_parent_pom, classes=comma_separated_classes)
    subprocess.run([cmd], shell=True)


def collect_submodules(path_to_pom: str) -> List[str]:
    """Returns a list of paths to every mvn submodule of the specified parent module."""
    cmd = "mvn -f {pom} -q --also-make exec:exec -Dexec.executable=\"pwd\"".format(pom=path_to_pom)
    completed_process = subprocess.run([cmd], stdout=subprocess.PIPE, encoding='utf-8', shell=True)
    return completed_process.stdout.splitlines()


def filter_target_modules(submodules: List[str]) -> List[str]:
    """Filters a list mvn submodule paths. Returns a list of paths to submodules that contain a target directory."""
    return list(filter(has_target_dir, submodules))


def has_target_dir(path: str) -> bool:
    """Returns True iff the specified directory contains a directory named 'target'"""
    sub_dirs = os.listdir(path)
    return const.MVN_TARGET_DIR in sub_dirs and os.path.isdir(os.path.join(path, const.MVN_TARGET_DIR))



def collect_surefire_reports(project_root: str) -> List[str]:
    """Returns a list of filenames for files containing test execution data."""
    path_to_reports = os.path.join(project_root, const.MVN_TARGET_DIR, const.SUREFIRE_REPORTS_DIR)
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


def write_log_list(log_list: List[Dict[str, Any]], path_to_log: str) -> str:
    """Writes a list of test data dicts to a JSON file in the specified dir and returns the path to the created file."""
    filename = log_list[0]['report']['test_name'] + '.json'
    path = os.path.join(path_to_log, filename)

    with open(path, 'w') as file:
        file.write(json.dumps(log_list, indent=2))
    
    return filename
