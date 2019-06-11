import sys
from typing import Dict

def warn(current_commit: str, next_commit: str, delta: float, threshold: float):
    print("WARNING: {} introduced performance change. Delta: {}. Threshold: {}.".format(current_commit, delta, threshold), file=sys.stderr)

def print_info(test_name: str, std_dev: float):
    print("\n{}\n\nStd deviation: {:.3f}\n".format(test_name, std_dev))


def print_header():
    print("{:<42}{:<9}{:<9}{:<5}".format('commit', 'runtime','delta', 'speedup'))


def log_delta(current_commit: str, runtime: float, delta: float, speedup: float):
    print("{:<42}{:<9.3f}{:<9.3f}{:<5.3f}".format(current_commit, runtime, delta, speedup))


def print_statistics(statistics: Dict):
    print("\n{s[test_name]}"
        "\n\nStd deviation: {s[std_dev]}"
        "\nDelta threshold: {s[delta_threshold]}"
        "\nStd deviation threshold: {s[std_dev_threshold]}\n".format(s=statistics))
    
    print_header()
    
    for commit_statistics in statistics['commits']:
        print("{c[hexsha]:<42}{c[runtime]:<9.3f}{c[runtime_delta]:<9.3f}{c[speedup]:<5.3f}".format(c=commit_statistics))
