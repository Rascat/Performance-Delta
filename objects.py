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
    scorePercentiles: Dict[str, float]


class JmhReport(NamedTuple):
    """Data structure that represent data obtained by a running a jmh benchmark"""
    benchmark: str
    mode: str
    threads: int
    forks: int
    jvm: str
    jvm_args: List[str]
    jdk_version: str
    warmup_iterations: int
    warmup_time: str
    measurement_iterations: int
    measurement_time: str
    primary_metric: PrimaryMetric


def build_commit_report(report_data: Dict[str, Any]) -> CommitReport:
    """Takes a dict with CommitReport fields as keys and returns the CommitReport equivalent"""
    report = JUnitReport(**report_data[const.REPORT])
    return CommitReport(commit=report_data[const.COMMIT], report=report)


def build_jmh_report(report_data_list: List[Dict[str, Any]]) -> JmhReport:
    """Builds a JmhReport object from the report data"""
    # get first, and only, element from list
    report_data = report_data_list[0]
    primary_metric = PrimaryMetric(**report_data['primaryMetric'])
    jmh_report = JmhReport(
        benchmark=report_data['benchmark'],
        mode=report_data['mode'],
        threads=report_data['threads'],
        forks=report_data['forks'],
        jvm=report_data['jvm'],
        jvm_args=report_data['jvmArgs'],
        jdk_version=report_data['jdkVersion'],
        warmup_iterations=report_data['warmupIterations'],
        warmup_time=report_data['warmupTime'],
        measurement_iterations=report_data['measurementIterations'],
        measurement_time=report_data['measurementTime'],
        primary_metric=primary_metric)
    return jmh_report


def create_commit_report(commit: str, report: JUnitReport) -> CommitReport:
    return CommitReport(commit=commit, report=report)


def create_junit_report(report_xml) -> JUnitReport:
    return JUnitReport(
        test_name=report_xml.name,
        test_run=report_xml.tests,
        time_elapsed=report_xml.time,
        failures=report_xml.failures,
        errors=report_xml.errors,
        skipped=report_xml.skipped)

