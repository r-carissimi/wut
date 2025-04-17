"""Plots results of the benchmarks"""

import json
import logging
import os

import matplotlib.pyplot as plt

from . import utils


def parse(parser):
    """Parse command-line arguments for the runtime module."""
    parser.add_argument(
        "results_file",
        help="Path to the results file to plot",
        type=str,
    )

    parser.add_argument(
        "--plots-folder",
        default="plots",
        help="Path to the folder where plots will be saved (default: plots)",
    )

    utils.add_log_level_argument(parser)

    return parser


def _load_results(file_path):
    """Load benchmark results from a JSON file."""
    try:
        with open(file_path, "r") as f:
            results = json.load(f)
            if not results:
                logging.info("No results found in the file.")
                return None
            return results
    except json.JSONDecodeError:
        logging.error("Failed to decode JSON from the results file.")
        return None


def _collect_benchmarks(results):
    """Collect and sort benchmark names."""
    benchmarks_set = set()
    for runtime in results.values():
        benchmarks_set.update(runtime.keys())
    return sorted(benchmarks_set)


def _determine_metrics(benchmarks_list, results):
    """Determine the metric to use for each benchmark.

    If any runtime has a score > 0, use score; otherwise, use elapsed_time.
    """

    benchmark_metrics = {}
    for benchmark in benchmarks_list:
        use_score = any(
            results[runtime].get(benchmark, {}).get("score", 0) > 0
            for runtime in results
        )
        benchmark_metrics[benchmark] = "score" if use_score else "elapsed_time"

    logging.debug(f"Benchmark metrics: {benchmark_metrics}")

    return benchmark_metrics


def _collect_raw_values(benchmarks_list, benchmark_metrics, results):
    """Collects values for each benchmark and runtime.

    What it does it taking the values from the results file in the following format:

    {
        "runtime1": {
            "benchmark1": {"elapsed_time": 1111, "score": 0},
            "benchmark2": {"elapsed_time": 2222, "score": 90},
        },
        "runtime2": {
            "benchmark1": {"elapsed_time": 3333, "score": 0},
            "benchmark2": {"elapsed_time": 4444, "score": 180},
        }
    }
    And collecting the values for each benchmark and runtime in a dictionary.
    The result will be a dictionary with the following format:

    {
        "benchmark1": {"runtime1": 1000, "runtime2": 3333},
        "benchmark2": {"runtime1": 90, "runtime2": 180}
    }
    """

    raw_values = {
        benchmark: {
            runtime: (data.get(metric, 0))
            for runtime, data in (
                (runtime, results[runtime].get(benchmark, {})) for runtime in results
            )
        }
        for benchmark, metric in ((b, benchmark_metrics[b]) for b in benchmarks_list)
    }

    logging.debug(f"Raw values collected: {raw_values}")

    return raw_values


def _normalize_values(benchmarks_list, benchmark_metrics, raw_values):
    """Normalize raw values for each benchmark.

    For scores, normalize by the maximum value.
    For elapsed times, normalize by the minimum value.
    """

    runtime_data = {
        runtime: {"values": {}} for runtime in raw_values[benchmarks_list[0]]
    }
    for benchmark in benchmarks_list:
        values = raw_values[benchmark]
        if benchmark_metrics[benchmark] == "score":
            logging.debug(f"Normalizing scores for {benchmark} with max value")
            max_val = max(values.values())
            for runtime, val in values.items():
                runtime_data[runtime]["values"][benchmark] = (
                    (val / max_val * 100) if max_val > 0 else 0
                )
        else:
            logging.debug(f"Normalizing elapsed times for {benchmark} with min value")
            min_val = min(val for val in values.values() if val > 0) or 1e-9
            for runtime, val in values.items():
                runtime_data[runtime]["values"][benchmark] = (
                    (val / min_val * 100) if val > 0 else 0
                )
    return runtime_data


def _plot_results(
    runtime_data, benchmarks_list, benchmark_metrics, results_file, plots_folder
):
    """Plot the normalized benchmark results and saves the file"""

    x = range(len(benchmarks_list))
    bar_width = 0.8 / len(runtime_data)
    colors = plt.cm.tab10.colors
    plt.figure(figsize=(16, 10))

    for i, (runtime, data) in enumerate(runtime_data.items()):
        y_values = [data["values"].get(benchmark, 0) for benchmark in benchmarks_list]
        plt.bar(
            [pos + i * bar_width for pos in x],
            y_values,
            bar_width,
            label=runtime,
            color=colors[i % len(colors)],
        )

    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.title("Benchmark Results Grouped by Runtime (Normalized %)")
    plt.ylabel("Normalized Metric Value (%)")
    plt.xlabel("Benchmark")
    plt.xticks(
        [pos + (len(runtime_data) - 1) * bar_width / 2 for pos in x],
        [f"{b}\n({benchmark_metrics[b]})" for b in benchmarks_list],
        rotation=45,
        ha="right",
    )
    plt.legend()
    plt.tight_layout()

    plot_filename = os.path.splitext(os.path.basename(results_file))[0] + ".png"
    plot_path = os.path.join(plots_folder, plot_filename)
    plt.savefig(plot_path)
    plt.close()
    logging.info(f"Saved grouped percentage plot to {plot_path}")


def main(args):
    logging.getLogger().setLevel(getattr(logging, args.log_level.upper()))
    os.makedirs(args.plots_folder, exist_ok=True)

    results = _load_results(args.results_file)
    if not results:
        return

    benchmarks_list = _collect_benchmarks(results)
    benchmark_metrics = _determine_metrics(benchmarks_list, results)
    raw_values = _collect_raw_values(benchmarks_list, benchmark_metrics, results)

    runtime_data = _normalize_values(benchmarks_list, benchmark_metrics, raw_values)
    _plot_results(
        runtime_data,
        benchmarks_list,
        benchmark_metrics,
        args.results_file,
        args.plots_folder,
    )
