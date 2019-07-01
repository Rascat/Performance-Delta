from typing import Dict, Any

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
