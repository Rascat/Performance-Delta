import subprocess
from typing import List


def run_mvn_test(path_to_pom: str,
                 test_classes: List[str] = None) -> None:
    """Triggers test execution with surefire for the maven project specified in the pom."""
    print('Running test suite of {pom}'.format(pom=path_to_pom))
    if test_classes is None:
        cmd = 'mvn clean test -f {pom} -q'.format(pom=path_to_pom)
    else:
        comma_separated_classes = ','.join(test_classes)
        cmd = 'mvn clean test -DfailIfNoTests=false -Dtest={classes} -am -f {pom} -q'.format(
            pom=path_to_pom, classes=comma_separated_classes)

    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError:
        print('Failed running test suite of project described by {pom}'.format(pom=path_to_pom))
        exit(1)


def run_mvn_install(path_to_pom: str) -> None:
    """Installs the specified project to the local maven repository"""
    print('Installing {pom} to local maven repository.'.format(
        pom=path_to_pom))
    cmd = 'mvn install -f {pom} -DskipTests -q'.format(pom=path_to_pom)

    # set findbugs version to 3.0.5 because maven 3.6.1 and findbugs<3.0.5 dont get along
    cmd += ' -Dplugin.maven-findbugs.version=3.0.5'

    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError:
        print('Could not install project described by {pom}'.format(pom=path_to_pom))
        exit(1)


def mvn_package(path_to_pom: str) -> None:
    print('Packaging {pom}.'.format(pom=path_to_pom))
    cmd = 'mvn -f {pom} package -q'.format(pom=path_to_pom)
    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError:
        print('Packing of project specified by {pom} failed.'.format(pom=path_to_pom))
        exit(1)


def mvn_set_dep_version(path_to_pom: str, group_id: str, version_nr: str) -> None:
    """Sets the required version of dependencies which belong to the specified group id"""
    print('Setting version of dependency  {group_id}.* to {version}'.format(
            group_id=group_id, version=version_nr))
    cmd = 'mvn -f {pom} versions:use-dep-version -Dincludes={group_id} -DdepVersion={version} -q'.format(
        pom=path_to_pom, group_id=group_id, version=version_nr)
    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError:
        print('Setting the version of group {group} to {version} failed.'.format(
            group=group_id, version=version_nr))
        exit(1)


def fetch_maven_project_version(path_to_pom: str) -> str:
    print('Fetching version number of {pom}'.format(pom=path_to_pom))
    cmd = ('mvn -f {pom} help:evaluate '
           '-Dexpression=project.version -q -DforceStdout').format(pom=path_to_pom)
    try:
        completed_process = subprocess.run(
            cmd, stdout=subprocess.PIPE, encoding='utf-8', shell=True, check=True)

        print('Fetched version nr.: {version}'.format(version=completed_process.stdout))
        return completed_process.stdout
    except subprocess.CalledProcessError:
        print('Failed version nr of project described by {pom}'.format(pom=path_to_pom))
        exit(1)