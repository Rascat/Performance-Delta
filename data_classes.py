from typing import Any, List

class SurefireReport:
    
    def __init__(self, test_run: int, failures: int, errors: int, skipped: int,
        time_elapsed: float, test_name: str) -> None:
        self.test_run = test_run
        self.failures = failures
        self.errors = errors
        self.skipped = skipped
        self.time_elapsed = time_elapsed

class BenchmarkStatistics:

    def __init__(self, test_name: str, std_dev: float,
        delta_threshold: float, commits: List[Any]) -> None:
        self.test_name = test_name
        self.std_dev = std_dev
        self.delta_threshold = delta_threshold
        self.commits = commits

class CommitStatistics:

    def __init__(self, current_commit: str, runtime: str, speedup: float,
        runtime_delta: float) -> None:
        self.current_commit = current_commit
        self.runtime = runtime
        self.speedup = speedup
        self.runtime_delta = runtime_delta
