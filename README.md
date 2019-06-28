# Regression Benchmarking

For an interval of commits in a given maven repository, run the whole test suite and log results

## Prerequisites

* Python 3.6

## Install

Clone the repository and create a virtual environment. (`python3 -m venv .env`).
Activate the environment and install the dependencies using `pip install -r requirements.txt`.

## Quickstart

The benchmarking data is obtained by issuing `mvn test` for a given maven project. For a single module project one could start the benchmarking process by executing `python path/to/main.py -p path/to/mvn-project commit-hash-start commit-hash-end`, where `commit-hash-start` ist the revision id of to commit to start benchmarking from (must be the later one) and `commit-hash-end` is the revision id of the commit to which the benchmarking process should go. Optionally, can specify which test classes to run with `-c ClassATest.java,ClassBTest.java,[...]`

By default, the resulting log files will be stored under the parent directory of the maven project in a directory called `perfdelta-results`.
If that is not feasible for the given use case, one can specify an output directory with `-d path/to/output-dir`.