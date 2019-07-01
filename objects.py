from typing import NamedTuple, List
import json
from utils import unpack


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
