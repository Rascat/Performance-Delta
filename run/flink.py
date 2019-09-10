import subprocess


def submit_to_flink(path_to_flink: str, path_to_jar, classname: str = None, args: str = None) -> None:
    """Submits job to flink cluster. Expects cluster is already running.

    :param path_to_flink Path to flink installation
    :param path_to_jar Path to jar containing submittable executable
    :param classname Name of submittable class
    :param args Arguments to be passed to the submittable class
    """
    print('Submitting jar {jar} to {flink}'.format(jar=path_to_jar, flink=path_to_flink))
    cmd = '{flink}/bin/flink run '.format(flink=path_to_flink)
    if classname is not None:
        cmd += '-c {classname} '.format(classname=classname)
    cmd += '{jar} '.format(jar=path_to_jar)
    if args is not None:
        cmd += args

    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError:
        print('Could not submit flink job')
        exit(1)
