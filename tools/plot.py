"""Plots results of the benchmarks"""

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

    results = utils.load_results_file(args.results_file)
    if not results:
        return

    benchmarks_list = utils.collect_benchmarks(results)
    benchmark_metrics = utils.determine_benchmark_metrics(results, benchmarks_list)
    raw_values = utils.transpose_benchmark_data(
        results, benchmarks_list, benchmark_metrics
    )

    runtime_data = _normalize_values(benchmarks_list, benchmark_metrics, raw_values)
    _plot_results(
        runtime_data,
        benchmarks_list,
        benchmark_metrics,
        args.results_file,
        args.plots_folder,
    )
