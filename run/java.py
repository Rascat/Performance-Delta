import subprocess


def run_jar(path_to_jar: str) -> None:
    """Runs an executable jar"""
    print('Running executable jar {jar}'.format(jar=path_to_jar))
    cmd = 'java -jar {jar}'.format(jar=path_to_jar)

    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError:
        print('Failed running executable jar {jar}'.format(jar=path_to_jar))
        exit(1)
