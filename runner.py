import json
import os.path
import subprocess
from typing import Dict, List

from git import Repo  # type: ignore
from junitparser import JUnitXml  # type: ignore

import const
import utils
from objects import CommitReport, JmhReport, build_jmh_report, create_commit_report, create_junit_report


def run(path_to_repo: str, path_to_log: str, commit_ids: List[str], is_interval: bool,
        branch: str, invocation_count: int, test_classes: List[str] = None):
    """Runs a maven repositories test suite over a range of commits and logs commit specific execution times."""
    repo = Repo(path_to_repo)
    path_to_parent_pom = os.path.join(path_to_repo, const.POM)

    # list of all commits in the specified branch
    commit_list = list(repo.iter_commits(branch))

    if is_interval:
        index_start = commit_list.index(repo.commit(commit_ids[0]))
        index_end = commit_list.index(repo.commit(commit_ids[1]))

        if index_start >= index_end:
            print('Error, wrong commit order. First commit must be more recent than the second one.')
            exit(1)

        # get last n commits, counting from HEAD
        selected_commits = commit_list[index_start: index_end + 1]
    else:
        # retrieve commit objects by id from the commit list
        selected_commits = list(
            map(lambda x: commit_list[commit_list.index(repo.commit(x))], commit_ids))

    utils.create_dir(path_to_log)

    commit_report_list = []  # type: List[CommitReport]
    jmh_report_list = []  # type: List[JmhReport]

    for commit in selected_commits:
        repo.git.checkout(commit.hexsha)

        generate_test_suite_metrics(commit_report_list, path_to_parent_pom, commit, invocation_count, test_classes)
        generate_pipeline_metrics(jmh_report_list, path_to_parent_pom, '~/Code/gradoop-jmh-pipeline')

    for grouped_list in group_commit_reports_by_test_name(commit_report_list):
        write_grouped_commit_reports(grouped_list, path_to_log)

    with open('jmh_reports.json', 'w') as file:
        file.write(json.dumps(utils.unpack(jmh_report_list), indent=2))

    # revert repo to original state
    repo.git.checkout(branch)


def run_jar(path_to_jar: str) -> None:
    """Runs an executable jar"""
    cmd = 'java -jar {jar}'.format(jar=path_to_jar)
    subprocess.run([cmd], shell=True)


def generate_test_suite_metrics(commit_report_list: List[CommitReport], path_to_parent_pom: str, commit,
                                invocation_count: int, test_classes: List[str]) -> None:
    """Runs the test suite and collects originating JUnit reports"""
    for i in range(invocation_count):
        run_mvn_test(path_to_parent_pom, test_classes=test_classes)

    submodules = filter_target_modules(
        collect_submodules(path_to_parent_pom))

    for submodule in submodules:
        filenames = collect_surefire_reports(submodule)
        for filename in filenames:
            report_xml = JUnitXml.fromfile(filename)
            report = create_junit_report(report_xml)
            commit_report = create_commit_report(commit=commit.hexsha, report=report)

            commit_report_list.append(commit_report)


def generate_pipeline_metrics(jmh_report_list: List[JmhReport], path_to_parent_pom: str, path_to_pipeline: str) -> None:
    """Runs the pipeline and collects originating JMH reports.

    It is assumed that the executable jar containing the benchmark can be found under pipeline_root/target/.
    It is further assumed that the resulting jmh-report is named after the default (jmh-result.json).
    """
    # install current revision
    run_mvn_install(path_to_parent_pom)
    # get version number
    version_nr = utils.fetch_maven_project_version(path_to_parent_pom)
    # build pipeline
    pipeline_pom = os.path.join(path_to_pipeline, 'pom.xml')
    utils.mvn_set_dep_version(pipeline_pom, 'org.gradoop', version_nr)
    utils.mvn_package(pipeline_pom)
    # execute pipeline
    jar_name = 'gradoop-pipeline-1.0-SNAPSHOT-shaded.jar'
    path_to_jar = os.path.join(path_to_pipeline, 'target', jar_name)
    run_jar(path_to_jar)

    # read jmh-result file
    with open('jmh-result.json') as file:
        data = json.load(file)
    # create JmhReport object
    jmh_report = build_jmh_report(data)
    jmh_report_list.append(jmh_report)


def run_mvn_test(path_to_parent_pom: str,
                 test_classes: List[str] = None) -> None:
    """Triggers test execution with surefire for the maven project specified in the pom."""
    print('Running test suite of {pom}'.format(pom=path_to_parent_pom))
    if test_classes is None:
        cmd = 'mvn clean test -f {pom} -q'.format(pom=path_to_parent_pom)
    else:
        comma_separated_classes = ','.join(test_classes)
        cmd = 'mvn clean test -DfailIfNoTests=false -Dtest={classes} -am -f {pom} -q'.format(
            pom=path_to_parent_pom, classes=comma_separated_classes)

    subprocess.run(cmd, shell=True)


def run_mvn_install(path_to_parent_pom: str) -> None:
    """Installs the specified project to the local maven repository"""
    print('Installing {pom} to local maven repository.'.format(
        pom=path_to_parent_pom))
    cmd = 'mvn install -f {pom} -DskipTests -q'.format(pom=path_to_parent_pom)

    subprocess.run(cmd, shell=True)


def collect_submodules(path_to_pom: str) -> List[str]:
    """Returns a list of paths to every mvn submodule of the specified parent module."""
    cmd = 'mvn -f {pom} -q --also-make exec:exec -Dexec.executable="pwd"'.format(
        pom=path_to_pom)
    completed_process = subprocess.run(
        cmd, stdout=subprocess.PIPE, encoding='utf-8', shell=True)
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

    Assumes that reports are located either under module-root/target/surefire-reports or
    module_root/target/surefire-reports/junitreports
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


def write_grouped_commit_reports(commit_reports: List[CommitReport], path_to_log: str) -> str:
    """Writes a list of test data dicts to a JSON file in the specified dir and returns the path to the created file.

    :param commit_reports: List of CommitReport objects
    :param path_to_log: Path to log dir
    :return: Name of the file the data was written to
    """
    filename = commit_reports[0].report.test_name + '.json'
    path = os.path.join(path_to_log, filename)

    with open(path, 'w') as file:
        file.write(json.dumps(utils.unpack(commit_reports), indent=2))

    return filename
