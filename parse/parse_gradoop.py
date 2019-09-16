import argparse
import csv
from statistics import mean
from typing import List, Dict, Any

from model.objects import BenchmarkReportRow


def parse_gradoop_benchmark_report(path_to_csv: str) -> List[BenchmarkReportRow]:
    with open(path_to_csv) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='|')
        next(csv_reader, None)  # skip the header

        benchmark_report_rows = []
        for line in csv_reader:
            parallelism = int(line[0])
            runtime = int(line[10])
            benchmark_report_row = BenchmarkReportRow(parallelism, runtime)
            benchmark_report_rows.append(benchmark_report_row)

        return benchmark_report_rows


def group_benchmark_report_by_parallelism(rows: List[BenchmarkReportRow]) -> Dict[int, Dict[str, Any]]:
    result = {}
    for row in rows:
        if row.parallelism not in result.keys():
            result[row.parallelism] = {'runtimes': [row.runtime]}
        else:
            result[row.parallelism]['runtimes'].append(row.runtime)

    return result


def compute_mean_runtime(report: Dict[int, Dict[str, Any]]) -> Dict[int, Dict[str, Any]]:
    for parallelism in report.keys():
        runtimes = report[parallelism]['runtimes']
        mean_runtime = round(mean(runtimes))
        report[parallelism]['mean_runtime'] = mean_runtime

    return report


def compute_speedup(report: Dict[int, Dict[str, Any]]) -> Dict[int, Dict[str, Any]]:
    if 1 not in report.keys():
        print('Could not compute speedup because no runtime data for parallelism one given.')
        return report

    base_runtime = report[1]['mean_runtime']

    for parallelism in report.keys():
        speedup = base_runtime / report[parallelism]['mean_runtime']
        report[parallelism]['speedup'] = speedup

    return report


def main():
    parser = argparse.ArgumentParser(
        description='Parse Gradoop Benchmark result and compute analytics')
    parser.add_argument('path', type=str, help='Path to csv')
    args = parser.parse_args()
    path = args.path

    report_rows = parse_gradoop_benchmark_report(path)
    grouped_report = group_benchmark_report_by_parallelism(report_rows)
    grouped_report = compute_mean_runtime(grouped_report)
    grouped_report = compute_speedup(grouped_report)
    print(grouped_report)


if __name__ == '__main__':
    main()
