"""Exports results to a CSV file."""

import csv
import logging
import os

from . import utils


def parse(parser):
    """Parse command-line arguments for the runtime module."""
    parser.add_argument(
        "results_file",
        help="Path to the results file to plot",
        type=str,
    )

    parser.add_argument(
        "--csv-folder",
        default="results",
        help="Path to the folder where CSVs will be saved (default: results)",
    )

    utils.add_log_level_argument(parser)

    return parser


def _write_benchmark_results_to_csv(data, metrics, filename):
    """
    Writes benchmark results from a nested dictionary to a CSV file.
    Benchmarks can have different sets of runtimes.

    The input dict format is:
    {
        "benchmark_name": {
            "runtime1": value1,
            "runtime2": value2,
            ...
        },
        ...
    }

    The output CSV will have headers: "benchmark", "wasmtime", "wasmer", ...

    Args:
        data (dict): Nested dictionary containing benchmark results.
                     The outer keys are benchmark names, and the inner
                     keys are runtime names.
        filename (str): The name of the CSV file to write to.
    """

    # Collecting all unique runtimes in order to create the header
    all_runtimes = set()
    for runtimes in data.values():
        all_runtimes.update(runtimes.keys())

    # Sorting runtimes for consistent order in the CSV
    all_runtimes = sorted(all_runtimes)

    logging.debug(f"Runtimes found in results: {all_runtimes}")

    # Writing to CSV (header first and then rows)
    with open(filename, mode="w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["benchmark"] + all_runtimes)
        for benchmark, runtimes in data.items():
            row = [benchmark + " (" + metrics[benchmark] + ")"] + [
                runtimes.get(rt, "") for rt in all_runtimes
            ]
            writer.writerow(row)

    logging.info(f"Results exported to {filename}")


def main(args):
    logging.getLogger().setLevel(getattr(logging, args.log_level.upper()))
    os.makedirs(args.csv_folder, exist_ok=True)

    args.results_file = utils.get_absolute_path(args.results_file)
    args.csv_folder = utils.get_absolute_path(args.csv_folder)

    results = utils.load_results_file(args.results_file)
    if not results:
        return

    benchmarks_list = utils.collect_benchmarks(results)
    benchmark_metrics = utils.determine_benchmark_metrics(results, benchmarks_list)
    raw_values = utils.transpose_benchmark_data(
        results, benchmarks_list, benchmark_metrics
    )

    # CSV filename is the same as the results file, but with a .csv extension
    filename = os.path.join(
        args.csv_folder,
        os.path.splitext(os.path.basename(args.results_file))[0] + ".csv",
    )

    _write_benchmark_results_to_csv(raw_values, benchmark_metrics, filename)
