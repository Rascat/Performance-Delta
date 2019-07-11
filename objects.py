from typing import NamedTuple, List, Any, Dict
import json
from utils import unpack
import const


class JUnitReport(NamedTuple):
    test_name: str
    test_run: int
    failures: int
    errors: int
    time_elapsed: float
    skipped: int


class CommitReport(NamedTuple):
    commit: str # commit revision id
    report: JUnitReport


class CommitStatistics(NamedTuple):
    hexsha: str
    runtime: float
    speedup: float
    runtime_delta: float


class BenchmarkStatistics(NamedTuple):
    test_name: str
    std_dev: float
    delta_threshold: float
    speedup_threshold: float
    commits: List[CommitStatistics]

    pass

def build_commit_report(report_data: Dict[str, Any]) -> CommitReport:
    """Takes a dict with CommitReport fields as keys and returns the CommitReport equivalent"""
    report = JUnitReport(**report_data[const.REPORT])
    return CommitReport(commit=report_data[const.COMMIT], report=report)