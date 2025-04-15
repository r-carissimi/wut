"""Runs benchmarks using runtimes"""

import json
import logging
import os
import re
import time

from . import benchmarks, runtime


def parse(parser):
    """Parse command-line arguments for the runtime module.

    Args:
        parser (ArgumentParser): The argument parser to add subcommands to.
    """

    parser.add_argument(
        "-r",
        "--runtimes",
        nargs="+",
        default=["all"],
        help="List of runtimes to use. Use 'all' to use all runtimes. Default: all",
    )

    parser.add_argument(
        "-b",
        "--benchmarks",
        nargs="+",
        default=["all"],
        help="""List of benchmarks to use. Use 'all' to use all benchmarks.
            You can choose both a group of benchmarks (e.g. coremark) as well
            as a specific one (e.g. coremark/coremark-1000) Default: all""",
    )

    parser.add_argument(
        "--benchmarks-folder",
        default="benchmarks",
        help="Path to the folder containing benchmarks (default: benchmarks)",
    )

    parser.add_argument(
        "--runtimes-file",
        default="runtimes/runtimes.json",
        help="Path to the JSON file containing runtimes (default: runtimes/runtimes.json)",
    )

    parser.add_argument(
        "--results-folder",
        default="results",
        help="Path to the folder where results will be saved (default: results)",
    )

    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level (default: INFO)",
    )

    return parser


def _get_runtimes_from_names(runtimes_list, file="runtimes/runtimes.json"):
    runtimes = []
    for runtime_name in runtimes_list:
        if runtime_name == "all":
            continue

        r = runtime.get_runtime_from_name(runtime_name, file)
        if r is not None:
            runtimes.append(r)

    return runtimes


def _get_benchmarks_from_names(benchmarks_list):
    benchs = dict()

    for benchmark_name in benchmarks_list:
        if benchmark_name == "all":
            continue

        b = benchmarks.get_benchmark_from_name(benchmark_name)
        if b is not None:
            for k, v in b.items():
                benchs.setdefault(k, []).extend(v)

    return benchs


def _get_benchmarks(benchmarks_list):
    """This function takes a dict of benchmark groups and returns a list of
    benchmarks, without their group. It also adds the group name to the
    path of each benchmark, thus having the full path for each benchmark in the
    object itself.

    This is the input format:

    {
        "group_name": [
            {
                "name": "benchmark1",
                "path": "path/to/benchmark1"
                ...
            },
            {
                "name": "benchmark2",
                "path": "path/to/benchmark2"
                ...
            },
            ...
        ],
        ""group_name2": [...]
    }

    This is the output format:

    [
        {
            "name": "benchmark1",
            "path": "group_name/path/to/benchmark1"
            ...
        },
        {
            "name": "benchmark2",
            "path": "group_name/path/to/benchmark2"
            ...
        },
        ...
    ]
    """

    return [
        {**b, "path": f"{group_name}/{b['path']}"}
        for group_name, group_list in benchmarks_list.items()
        for b in group_list
    ]


def _parse_score(output, score_parser):
    match = re.search(score_parser, output)
    if match:
        return float(match.group("score"))
    return 0


def _run_benchmark_with_runtime(benchmark, runtime, benchmarks_folder):
    """Run a benchmark with a given runtime.

    Args:
        benchmark (dict): The benchmark to run.
        runtime (dict): The runtime to use.

    Returns:
        tuple: A tuple containing
               * elapsed time: The elapsed time of the benchmark in nanoseconds
               * score: The score of the benchmark (if applicable)
               * return code: The return code of the benchmark
               * output: The output of the benchmark as a string
    """

    benchmark_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        benchmarks_folder,
        benchmark["path"],
    )

    logging.debug(f"Running '{runtime['command']} {benchmark_path}'")

    start_time = time.perf_counter_ns()
    process = os.popen(f"{runtime['command']} {benchmark_path}")
    output = process.read()
    end_time = time.perf_counter_ns()
    elapsed_time = end_time - start_time

    return_code = process.close() or 0

    logging.debug(f"Output: {output}")

    score = 0
    if benchmark["score-parser"] is not None:
        score = _parse_score(output, benchmark["score-parser"])

    return elapsed_time, score, return_code, output


def _save_results_to_file(results, folder="results"):
    if not os.path.exists(folder):
        os.makedirs(folder)

    filename = os.path.join(folder, time.strftime("%Y-%m-%d_%H-%M-%S.json"))
    with open(filename, "w") as f:
        json.dump(results, f, indent=4)

    logging.info(f"Results saved to {filename}")


def main(args):
    logging.getLogger().setLevel(getattr(logging, args.log_level.upper()))

    # Get the runtime objects from the command line arguments
    runtimes_list = args.runtimes
    if runtimes_list == ["all"]:
        runtimes_list = runtime.list_runtimes(file=args.runtimes_file)
    else:
        runtimes_list = _get_runtimes_from_names(runtimes_list, file=args.runtimes_file)

    # If path to the runtimes is not absolute, prepend the path to the runtimes folder
    for r in runtimes_list:
        if not os.path.isabs(r["command"]):
            r["command"] = os.path.join(
                os.path.dirname(os.path.abspath(args.runtimes_file)),
                r["command"],
            )

    logging.debug(f"Using runtimes: {[r['name'] for r in runtimes_list]}")

    # Get the benchmark objects from the command line arguments
    benchmarks_list = args.benchmarks
    if benchmarks_list == ["all"]:
        benchmarks_list = benchmarks.list_benchmarks()
    else:
        benchmarks_list = _get_benchmarks_from_names(benchmarks_list)

    logging.debug(f"Using benchmarks: {benchmarks_list}")

    # Run the benchmarks with the runtimes
    results = dict()

    for r in runtimes_list:
        logging.debug(f"Using runtime: {r['name']}")
        results[r["name"]] = dict()
        for b in _get_benchmarks(benchmarks_list):
            logging.info(f"Running benchmark: {b['name']} with runtime: {r['name']}")

            elapsed_time, score, return_code, _ = _run_benchmark_with_runtime(
                b, r, args.benchmarks_folder
            )

            logging.info(f"Elapsed time: {elapsed_time} ns")
            logging.info(f"Score: {score}")
            logging.debug(f"Return code: {return_code}")
            if return_code != 0:
                logging.warning(
                    f"Benchmark {b['name']} failed with return code {return_code}"
                )
                elapsed_time = 0
                score = 0

            results[r["name"]][b["name"]] = {
                "elapsed_time": elapsed_time,
                "score": score,
            }

    logging.debug(f"Results: {results}")

    _save_results_to_file(results, folder=args.results_folder)
