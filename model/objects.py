from typing import NamedTuple, List, Any, Dict

import const


class JUnitReport(NamedTuple):
    """Data structure that holds the data of JUnit report file"""
    test_name: str
    test_run: int
    failures: int
    errors: int
    time_elapsed: float
    skipped: int


class JUnitCommitReport(NamedTuple):
    """Data structure that links a JUnit report to a specific commit id"""
    commit_id: str  # commit revision id
    report: JUnitReport


class JUnitStatistics(NamedTuple):
    """Data structure that holds computed statistics of a test suite for a given commit"""
    commit_id: str
    runtime: float
    speedup: float
    runtime_delta: float


class JmhStatistics(NamedTuple):
    commit_id: str
    mode: str
    score: float
    delta: float


class BenchmarkStatistics(NamedTuple):
    """Data structure that links benchmark specifics to a list of JUnitStatistics"""
    test_name: str
    std_dev: float
    delta_threshold: float
    speedup_threshold: float
    junit_statistics: List[JUnitStatistics]


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
    jvmArgs: List[str]
    jdkVersion: str
    warmupIterations: int
    warmupTime: str
    measurementIterations: int
    measurementTime: str
    primaryMetric: PrimaryMetric


class JmhCommitReport(NamedTuple):
    commit_id: str
    jmh_report: JmhReport


def build_junit_commit_report(report_data: Dict[str, Any]) -> JUnitCommitReport:
    """Takes a dict with CommitReport fields as keys and returns the CommitReport equivalent"""
    report = JUnitReport(**report_data[const.REPORT])
    return JUnitCommitReport(commit_id=report_data[const.COMMIT], report=report)


def build_jmh_report(report_data: Dict[str, Any]) -> JmhReport:
    """Builds a JmhReport object from the report data"""
    primary_metric = PrimaryMetric(**report_data['primaryMetric'])
    jmh_report = JmhReport(
        benchmark=report_data['benchmark'],
        mode=report_data['mode'],
        threads=report_data['threads'],
        forks=report_data['forks'],
        jvm=report_data['jvm'],
        jvmArgs=report_data['jvmArgs'],
        jdkVersion=report_data['jdkVersion'],
        warmupIterations=report_data['warmupIterations'],
        warmupTime=report_data['warmupTime'],
        measurementIterations=report_data['measurementIterations'],
        measurementTime=report_data['measurementTime'],
        primaryMetric=primary_metric)
    return jmh_report


def build_jmh_commit_report(commit_report_data: Dict[str, Any]) -> JmhCommitReport:
    return JmhCommitReport(commit_id=commit_report_data['commit_id'],
                           jmh_report=build_jmh_report(commit_report_data['jmh_report']))


def create_junit_commit_report(commit: str, report: JUnitReport) -> JUnitCommitReport:
    """Creates a CommitReport obj by associating a commit id with a JUnitReport"""
    return JUnitCommitReport(commit_id=commit, report=report)


def create_junit_report(report_xml) -> JUnitReport:
    """Creates a JUnitReport obj"""
    return JUnitReport(
        test_name=report_xml.name,
        test_run=report_xml.tests,
        time_elapsed=report_xml.time,
        failures=report_xml.failures,
        errors=report_xml.errors,
        skipped=report_xml.skipped)
