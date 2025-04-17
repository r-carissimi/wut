import json
import logging


def add_log_level_argument(parser):
    """Add a --log-level argument to the parser."""

    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level (default: INFO)",
    )

    return parser


def load_results_file(file_path):
    """Load benchmark results from a JSON file.

    Args:
        file_path (str): Path to the JSON file containing benchmark results.

    Returns:
        dict: Parsed benchmark results. If the file is empty or cannot be parsed,
              returns None.
    """
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


def collect_benchmarks(results):
    """Collect and sort benchmark names.

    Args:
        results (dict): Parsed benchmark results. If results is empty, an empty list is returned.

        The expected format is:
        {
            "runtime1": {
                "benchmark1": {...},
                "benchmark2": {...},
            },
            "runtime2": {
                "benchmark1": {...},
                "benchmark2": {...},
            }
        }

    Returns:
        list: Sorted list of unique benchmark names.
    """

    if not results:
        logging.info("No results found.")
        return []

    benchmarks_set = set()
    for runtime in results.values():
        benchmarks_set.update(runtime.keys())
    return sorted(benchmarks_set)


def transpose_benchmark_data(results, benchmarks_list, benchmark_metrics):
    """This function collects values for each benchmark and runtime (using the metric
    defined in benchmark_metrics) and transposes the data.

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

    And outputs it in the following format (note that just the values
    corresponding to the metric selected are kept):

    {
        "benchmark1": {"runtime1": 1000, "runtime2": 3333},
        "benchmark2": {"runtime1": 90, "runtime2": 180}
    }

    Args:
        results (dict): Parsed benchmark results.
        benchmarks_list (list): List of benchmark names.
        benchmark_metrics (dict): Dictionary mapping benchmark names to their respective metric ("score" or "elapsed_time").

    Returns:
        dict: Transposed benchmark data.
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


def determine_benchmark_metrics(results, benchmarks_list):
    """Determine the metric to use for each benchmark.
    If any runtime has a score > 0, use score; otherwise, use elapsed_time.

    Args:
        results (dict): Parsed benchmark results.
        benchmarks_list (list): List of benchmark names.

    Returns:
        dict: Dictionary mapping benchmark names to their respective metric ("score" or "elapsed_time").
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
