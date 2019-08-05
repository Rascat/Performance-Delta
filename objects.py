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
    commit: str  # commit revision id
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


class PrimaryMetric(NamedTuple):
    """Represents the primary metrics obtained by a jmh benchmark"""
    score: float
    scoreError: float
    scoreConfidence: List[float]
    scoreUnit: str
    rawData: List[List[float]]


class JmhReport(NamedTuple):
    """Data structure that represent data obtained by a running a jmh benchmark"""
    benchmark: str
    mode: str
    thread: int
    forks: int
    jvm: str
    jvmArgs: List[str]
    jdkVersion: str
    warmupIterations: int
    warmupTime: str
    measurementIterations: int
    measurementTime: str
    PrimaryMetric: PrimaryMetric


def build_commit_report(report_data: Dict[str, Any]) -> CommitReport:
    """Takes a dict with CommitReport fields as keys and returns the CommitReport equivalent"""
    report = JUnitReport(**report_data[const.REPORT])
    return CommitReport(commit=report_data[const.COMMIT], report=report)
