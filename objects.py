from typing import NamedTuple

class Statistics(NamedTuple):
    runtime: float
    delta: float

class JUnitReport(NamedTuple):
    test_name: str
    test_run: int
    failures: int
    errors: int
    time_elapsed: float
    skipped: int


s = Statistics(3.2, 4.2)
j = JUnitReport(
    test_name='some test',
    test_run=21,
    failures=21,
    errors=2,
    time_elapsed=3.21,
    statistics=s)
print(dict(j._asdict()))

