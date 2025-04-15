"""Plots results of the benchmarks"""

import json
import logging
import os

import matplotlib.pyplot as plt


def parse(parser):
    """Parse command-line arguments for the runtime module.

    Args:
        parser (ArgumentParser): The argument parser to add subcommands to.
    """

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

    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level (default: INFO)",
    )

    return parser


def main(args):
    logging.getLogger().setLevel(getattr(logging, args.log_level.upper()))

    os.makedirs(args.plots_folder, exist_ok=True)

    # Loads the results from the JSON file
    results = None
    with open(args.results_file, "r") as f:
        try:
            results = json.load(f)

            if not results:
                logging.info("No results found in the file.")
                return

        except json.JSONDecodeError:
            logging.error("Failed to decode JSON from the results file.")
            return

    logging.debug(f"Loaded results: {results}")

    # Collect benchmark names
    benchmarks_set = set()
    for runtime in results.values():
        benchmarks_set.update(runtime.keys())
    benchmarks_list = sorted(benchmarks_set)

    # Determine metric per benchmark
    benchmark_metrics = {}
    for benchmark in benchmarks_list:
        use_score = any(
            results[runtime].get(benchmark, {}).get("score", 0) > 0
            for runtime in results
        )
        benchmark_metrics[benchmark] = "score" if use_score else "elapsed_time"

    logging.debug(f"Benchmark metrics: {benchmark_metrics}")

    # Collect and normalize data
    runtime_data = {runtime: {"values": {}} for runtime in results}
    raw_values = {benchmark: {} for benchmark in benchmarks_list}

    for benchmark in benchmarks_list:
        metric = benchmark_metrics[benchmark]
        fallback = "elapsed_time" if metric == "score" else "score"

        # Collect raw values
        for runtime in results:
            data = results[runtime].get(benchmark, {})
            value = data.get(metric, 0)

            if value == 0 and fallback in data:
                value = data.get(fallback, 0)
                logging.warning(
                    f"{runtime}::{benchmark} missing {metric}, using fallback {fallback}"
                )

            raw_values[benchmark][runtime] = value

    # Normalize values
    for benchmark in benchmarks_list:
        values = raw_values[benchmark]
        if benchmark_metrics[benchmark] == "score":
            logging.debug(f"Normalizing scores for {benchmark} with max value")
            max_val = max(values.values())
            for runtime, val in values.items():
                norm = (val / max_val * 100) if max_val > 0 else 0
                runtime_data[runtime]["values"][benchmark] = norm
        else:
            logging.debug(f"Normalizing elapsed times for {benchmark} with min value")
            min_val = min(val for val in values.values() if val > 0) or 1e-9
            for runtime, val in values.items():
                norm = (val / min_val * 100) if val > 0 else 0
                runtime_data[runtime]["values"][benchmark] = norm

    # Plotting
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

    # Save the plot
    plot_filename = os.path.splitext(os.path.basename(args.results_file))[0] + ".png"
    plot_path = os.path.join(args.plots_folder, plot_filename)
    plt.savefig(plot_path)
    plt.close()

    logging.info(f"Saved grouped percentage plot to {plot_path}")
