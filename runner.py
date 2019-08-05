import glob
import json
import os.path
import subprocess
from pathlib import Path
from typing import Dict, List

from git import Repo  # type: ignore
from junitparser import JUnitXml  # type: ignore

import const
import utils
from objects import CommitReport, JUnitReport


def run(path_to_repo: str, path_to_log: str,
        commit_ids: List[str], is_interval: bool, branch: str, invocation_count: int, test_classes: List[str] = None):
    """Runs a maven repositories test suite over a range of commits and logs commit specific execution times."""
    repo = Repo(path_to_repo)
    path_to_parent_pom = os.path.join(path_to_repo, const.POM)

    # list of all commits in the specified branch
    commit_list = list(repo.iter_commits(branch))

    if is_interval:
        index_start = commit_list.index(repo.commit(commit_ids[0]))
        index_end = commit_list.index(repo.commit(commit_ids[1]))

        if (index_start >= index_end):
            print(
                "Error, wrong commit order. First commit must be younger than the second one.")
            exit(1)

        # get last n commits, counting from HEAD
        selected_commits = commit_list[index_start: index_end + 1]
    else:
        # retrieve commit objects by id from the commit list
        selected_commits = list(
            map(lambda x: commit_list[commit_list.index(repo.commit(x))], commit_ids))

    utils.create_dir(path_to_log)

    commit_report_list = []  # type: List[CommitReport]

    for commit in selected_commits:
        repo.git.checkout(commit.hexsha)

        for i in range(invocation_count):
            run_mvn_test(path_to_parent_pom, test_classes=test_classes)

        submodules = filter_target_modules(
            collect_submodules(path_to_parent_pom))

        for submodule in submodules:
            filenames = collect_surefire_reports(submodule)
            for filename in filenames:
                report_xml = JUnitXml.fromfile(filename)
                report = create_junit_report(report_xml)
                commit_report = create_commit_report(
                    commit=commit.hexsha, report=report)

                commit_report_list.append(commit_report)

        # install current revision
        run_mvn_install(path_to_parent_pom)
        # get version number
        version_nr = utils.fetch_maven_project_version(path_to_parent_pom)
        # build pipeline
        path_to_pipeline = '/home/lulu/Code/gradooppipeline/pom.xml'
        utils.mvn_set_dep_version(path_to_pipeline, 'org.gradoop', version_nr)
        utils.mvn_package(path_to_pipeline)
        # execute pipeline
        utils.mvn_exec_java(path_to_pipeline)

    for grouped_list in group_commit_reports_by_test_name(commit_report_list):
        write_grouped_commit_reports(grouped_list, path_to_log)

    # checkout HEAD again
    repo.git.checkout(branch)


def run_jmh_benchmark(path_to_jar: str, forks: int, result_format: str, result_name: str) -> None:
    cmd = 'java -jar {jar} -f {forks} -rf {result_format} -r {result_name}'.format(
        jar=path_to_jar, forks=forks, result_format=result_format, result_name=result_name)
    subprocess.run([cmd], shell=True)


def run_mvn_test(path_to_parent_pom: str,
                 test_classes: List[str] = None) -> None:
    """Triggers test execution with surefire for the maven project specified in the pom."""
    print('Running test suite of {pom}'.format(pom=path_to_parent_pom))
    if test_classes is None:
        cmd = "mvn clean test -f {pom} -q".format(pom=path_to_parent_pom)
    else:
        comma_separated_classes = ",".join(test_classes)
        cmd = "mvn clean test -DfailIfNoTests=false -Dtest={classes} -am -f {pom} -q".format(
            pom=path_to_parent_pom, classes=comma_separated_classes)

    subprocess.run([cmd], shell=True)


def run_mvn_install(path_to_parent_pom: str) -> None:
    """Installs the specified project to the local maven repository"""
    print(
        'Installing {pom} to local maven repository.'.format(
            pom=path_to_parent_pom))
    cmd = 'mvn install -f {pom} -DskipTests -q'.format(pom=path_to_parent_pom)

    subprocess.run([cmd], shell=True)


def collect_submodules(path_to_pom: str) -> List[str]:
    """Returns a list of paths to every mvn submodule of the specified parent module."""
    cmd = "mvn -f {pom} -q --also-make exec:exec -Dexec.executable=\"pwd\"".format(
        pom=path_to_pom)
    completed_process = subprocess.run(
        [cmd], stdout=subprocess.PIPE, encoding='utf-8', shell=True)
    return completed_process.stdout.splitlines()


def filter_target_modules(submodules: List[str]) -> List[str]:
    """Filters a list mvn submodule paths. Returns a list of paths to submodules that contain a target directory."""
    return list(filter(has_target_dir, submodules))


def has_target_dir(path: str) -> bool:
    """Returns True iff the specified directory contains a directory named 'target'"""
    sub_dirs = os.listdir(path)
    return const.MVN_TARGET_DIR in sub_dirs and os.path.isdir(
        os.path.join(path, const.MVN_TARGET_DIR))


def collect_surefire_reports(project_root: str) -> List[str]:
    """Returns a list of filenames for files containing test execution data.

    Assumes that reports are located either under module-root/target/surefire-reports or module_root/target/surefire-reports/junitreports
    """
    path_to_reports = os.path.join(
        project_root, const.MVN_TARGET_DIR, const.SUREFIRE_REPORTS_DIR, 'junitreports')
    if not os.path.isdir(path_to_reports):
        path_to_reports = os.path.join(
            project_root, const.MVN_TARGET_DIR, const.SUREFIRE_REPORTS_DIR)

    return utils.get_filenames_by_type(path_to_reports, 'xml')


def group_commit_reports_by_test_name(
        commit_reports: List[CommitReport]) -> List[List[CommitReport]]:
    """
    Groups a list of CommitReport objects like [{'test_name': 'X'},{'test_name': 'Y'}, {'test_name': 'X'}]
    to a list of lists like [[{'test_name': 'X'}, {'test_name': 'X'}], [{'test_name': 'Y'}]]
    """
    grouped_commit_reports = []  # type: List[List[CommitReport]]
    test_result_map = {}  # type: Dict[str, List[CommitReport]]

    for commit_report in commit_reports:
        test_name = commit_report.report.test_name

        if test_name not in test_result_map.keys():
            test_result_map[test_name] = [commit_report]
        else:
            test_result_map[test_name].append(commit_report)

    for key in test_result_map.keys():
        grouped_commit_reports.append(test_result_map[key])

    return grouped_commit_reports


def write_grouped_commit_reports(
        commit_reports: List[CommitReport], path_to_log: str) -> str:
    """Writes a list of test data dicts to a JSON file in the specified dir and returns the path to the created file."""
    filename = commit_reports[0].report.test_name + '.json'
    path = os.path.join(path_to_log, filename)

    with open(path, 'w') as file:
        file.write(json.dumps(utils.unpack(commit_reports), indent=2))

    return filename


def create_junit_report(report_xml) -> JUnitReport:
    return JUnitReport(
        test_name=report_xml.name,
        test_run=report_xml.tests,
        time_elapsed=report_xml.time,
        failures=report_xml.failures,
        errors=report_xml.errors,
        skipped=report_xml.skipped)


def create_commit_report(commit: str, report: JUnitReport) -> CommitReport:
    return CommitReport(commit=commit, report=report)
