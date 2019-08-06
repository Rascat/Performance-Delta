import glob
import os.path
from typing import List
import subprocess

import const


def get_parent_dir(child_dir: str) -> str:
    """Returns path to parent dir of the specified dir."""
    return os.path.abspath(os.path.join(child_dir, os.pardir))


def get_default_log_dir(path_to_repo: str) -> str:
    """Returns path to dir where test execution data and statistics are being written to."""
    parent_dir = get_parent_dir(path_to_repo)
    return os.path.join(parent_dir, const.RESULTS_DIRECTORY)


def get_filenames_by_type(path: str, filetype: str) -> List[str]:
    """Returns a list of filenames for files of the specified type in the given dir."""
    return glob.glob(path + os.path.sep + "*." + filetype)


def create_dir(path: str) -> str:
    """Creates the specified directory if it is not already present."""

    if not os.path.isdir(path):
        try:
            os.mkdir(path)
        except OSError:
            print("Creation of the directory %s failed" % path)
        else:
            print("Successfully created the directory %s" % path)

    return path


def is_named_tuple(x):
    """Copy pasted from stack overflow

    https://stackoverflow.com/questions/33181170/how-to-convert-a-nested-namedtuple-to-a-dict
    """
    _type = type(x)
    bases = _type.__bases__
    if len(bases) != 1 or bases[0] != tuple:
        return False
    fields = getattr(_type, '_fields', None)
    if not isinstance(fields, tuple):
        return False
    return all(isinstance(i, str) for i in fields)


def unpack(obj):
    """Copy pasted from stack overflow

    https://stackoverflow.com/questions/33181170/how-to-convert-a-nested-namedtuple-to-a-dict
    """
    if isinstance(obj, dict):
        return {key: unpack(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [unpack(value) for value in obj]
    elif is_named_tuple(obj):
        return {key: unpack(value) for key, value in obj._asdict().items()}
    elif isinstance(obj, tuple):
        return tuple(unpack(value) for value in obj)
    else:
        return obj


def fetch_maven_project_version(path_to_pom: str) -> str:
    print('Fetching version number of {pom}'.format(pom=path_to_pom))
    cmd = "mvn -f {pom} org.apache.maven.plugins:maven-help-plugin:3.1.0:evaluate -Dexpression=project.version -q -DforceStdout".format(
        pom=path_to_pom)
    completed_process = subprocess.run(
        [cmd],
        stdout=subprocess.PIPE,
        encoding='utf-8',
        shell=True)
    return completed_process.stdout


def mvn_set_dep_version(path_to_pom: str, group_id: str,
                        version_nr: str) -> None:
    print(
        "Setting version of dependency  {group_id}.* to {version}".format(
            group_id=group_id,
            version=version_nr))
    cmd = 'mvn -f {pom} versions:use-dep-version -Dincludes={group_id} -DdepVersion={version}'.format(
        pom=path_to_pom, group_id=group_id, version=version_nr)

    subprocess.run([cmd], shell=True)


def mvn_package(path_to_pom: str) -> None:
    print("Packaging {pom}.".format(pom=path_to_pom))
    cmd = 'mvn -f {pom} package -q'.format(pom=path_to_pom)
    subprocess.run([cmd], shell=True)
