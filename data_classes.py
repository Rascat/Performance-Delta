from typing import Any, List

class SurefireReport:
    
    """def __init__(self, test_run: int = None, failures: int = None, errors: int = None, skipped: int = None,
        time_elapsed: float = None, test_name: str = None) -> None:
        self._test_name = test_name
        self._test_run = test_run
        self._failures = failures
        self._errors = errors
        self._skipped = skipped
        self._time_elapsed = time_elapsed"""
    
    def __init__(self) -> None:
        pass

    @property
    def test_name(self) -> str:
        return self._test_name

    @test_name.setter
    def test_name(self, test_name: str) -> None:
        self._test_name = test_name
    
    @property
    def test_run(self) -> int:
        return self._test_run

    @test_run.setter
    def test_run(self, test_run: int) -> None:
        self._test_run = test_run

    @property
    def failures(self) -> int:
        return self._failures
    
    @failures.setter
    def failures(self, failures: int) -> None:
        self._failures = failures

    @property
    def errors(self) -> int:
        return self._errors
    
    @errors.setter
    def errors(self, errors) -> None:
        self._errors = errors
    
    @property
    def skipped(self) -> int:
        return self._skipped
    
    @skipped.setter
    def skipped(self, skipped) -> None:
        self._skipped = skipped
    
    @property
    def time_elapsed(self) -> float:
        return self._time_elapsed
    
    @time_elapsed.setter
    def time_elapsed(self, time_elapsed) -> None:
        self._time_elapsed = time_elapsed


class BenchmarkStatistics:

    def __init__(self) -> None:
        pass
    
    @property
    def test_name(self) -> str:
        return self._test_name
    
    @test_name.setter
    def test_name(self, test_name: str) -> None:
        self._test_name = test_name
    
    @property
    def std_dev(self) -> float:
        return self._std_dev
    
    @std_dev.setter
    def std_dev(self, std_dev: float) -> None:
        self._std_dev = std_dev
    
    @property
    def delta_threshold(self) -> float:
        return self._delta_threshold
    
    @delta_threshold.setter
    def delta_threshold(self, delta_threshold: float) -> None:
        self._delta_threshold = delta_threshold
    
    @property
    def commits(self) -> List[Any]:
        return self._commits
    
    @commits.setter
    def commtis(self, commits: List[Any]) -> None:
        self._commits = commits

class CommitStatistics:

    def __init__(self, current_commit: str, runtime: str, speedup: float,
        runtime_delta: float) -> None:
        self.current_commit = current_commit
        self.runtime = runtime
        self.speedup = speedup
        self.runtime_delta = runtime_delta
    
    @property
    def current_commit(self) -> str:
        return self._current_commit
    
    @current_commit.setter
    def current_commit(self, current_commit: str) -> None:
        self._current_commit = current_commit
    
    @property
    def runtime(self) -> str:
        return self._runtime
    
    @runtime.setter
    def runtime(self, runtime: str) -> None:
        self._runtime = runtime
    
    @property
    def speedup(self) -> float:
        return self._runtime
    
    @speedup.setter
    def speedup(self, speedup: float) -> None:
        self._speedup = speedup
    
    @property
    def runtime_delta(self) -> float:
        return self._runtime_delta
    
    @runtime_delta.setter
    def runtime_delta(self, runtime_delta: float) -> None:
        self._runtime_delta = runtime_delta
