from typing import Dict, Any

def parse_report(path_to_report: str) -> Dict:
    """
    Assumes surefire report is formatted as follows:

    -------------------------------------------------------------------------------
    Test set: org.rascat.TermsOfSumTest
    -------------------------------------------------------------------------------
    Tests run: 1, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.049 s - in org.rascat.TermsOfSumTest
    """
    line_list = [line.rstrip('\n') for line in open(path_to_report)]
    line_test_info = line_list[3]
    line_test_info = line_test_info.strip()
    test_data = line_test_info.split(' ')

    tests_run = int(test_data[2].rstrip(','))
    failures = int(test_data[4].rstrip(','))
    errors = int(test_data[6].rstrip(','))
    skipped = int(test_data[8].rstrip(','))
    time_elapsed = float(test_data[11].rstrip(','))
    test_name = test_data[15]

    return {
        "test_run": tests_run,
        "failures": failures,
        "errors": errors,
        "skipped": skipped,
        "time_elapsed": time_elapsed,
        "test_name": test_name
    }

def parse_junit_xml(junit_xml) -> Dict[str, Any]:
    """Parses a junitparser JUnitXml object and returns a dict."""
    return {
        'test_name': junit_xml.name,
        'time_elapsed': junit_xml.time,
        'test_run': junit_xml.tests,
        'failures': junit_xml.failures,
        'errors': junit_xml.errors,
        'skipped': junit_xml.skipped
    }
