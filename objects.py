from typing import NamedTuple, List, Any, Dict
import json
from utils import unpack
import const


class JUnitReport(NamedTuple):
    """Data structure that holds the data of JUnit report file"""
    test_name: str
    test_run: int
    failures: int
    errors: int
    time_elapsed: float
    skipped: int


class CommitReport(NamedTuple):
    """Data structure that links a JUnit report to a specific commit id"""
    commit: str # commit revision id
    report: JUnitReport


class CommitStatistics(NamedTuple):
    """Data structure that holds computed statistics of a test suite for a given commit"""
    hexsha: str
    runtime: float
    speedup: float
    runtime_delta: float


class BenchmarkStatistics(NamedTuple):
    """Data structure that links benchmark specifics to a list of CommitStatistics"""
    test_name: str
    std_dev: float
    delta_threshold: float
    speedup_threshold: float
    commits: List[CommitStatistics]


def build_commit_report(report_data: Dict[str, Any]) -> CommitReport:
    """Takes a dict with CommitReport fields as keys and returns the CommitReport equivalent"""
    report = JUnitReport(**report_data[const.REPORT])
    return CommitReport(commit=report_data[const.COMMIT], report=report)