"""Runs benchmarks using runtimes

This module provides a command-line interface to run benchmarks using
different runtimes. It allows users to specify which benchmarks and
runtimes to use, and saves the results to a specified folder.
"""

import json
import logging
import os
import re
import time

from . import benchmarks, runtimes, utils


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
        "--no-store-output",
        action="store_true",
        default=False,
        help="Do not save the output of the benchmarks to the results file (default: False)",
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
        "--repeat",
        type=int,
        default=1,
        help="Number of times to repeat each benchmark (default: 1)",
    )

    utils.add_log_level_argument(parser)

    return parser


def _filter_runtimes_by_name(selected_runtimes, runtimes_list):
    """Returns only the runtimes that are in the selected_runtimes list."""

    filtered_runtimes = []
    for runtime in runtimes_list:
        if runtime["name"] in selected_runtimes:
            filtered_runtimes.append(runtime)
    return filtered_runtimes


def _get_benchmarks_from_names(benchmarks_list, benchmarks_folder="benchmarks"):
    benchs = dict()

    for benchmark_name in benchmarks_list:
        b = benchmarks.get_benchmark_from_name(benchmark_name, benchmarks_folder)
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


def _run_benchmark_with_runtime(
    benchmark, runtime, benchmarks_folder, precompiled_path=None
):
    """Run a benchmark with a given runtime.

    Args:
        benchmark (dict): The benchmark to run.
        runtime (dict): The runtime to use.
        benchmarks_folder (str): The folder containing the benchmarks. Can
                                 be relative or absolute.
        precompiled_path (str): Path to the precompiled AOT file, if applicable.

    Returns:
        tuple: A tuple containing
               * elapsed time: The elapsed time of the benchmark in nanoseconds
               * score: The score of the benchmark (if applicable)
               * return code: The return code of the benchmark
               * output: The output of the benchmark as a string
    """

    benchmarks_folder = utils.get_absolute_path(benchmarks_folder)

    benchmark_path = os.path.join(
        benchmarks_folder,
        benchmark["path"],
    )

    if precompiled_path:
        benchmark_path = precompiled_path

    logging.debug(f"Running '{runtime['command']} {benchmark_path}'")

    start_time = time.perf_counter_ns()
    process = os.popen(f"{runtime['command']} {benchmark_path}")
    output = process.read()
    end_time = time.perf_counter_ns()
    elapsed_time = end_time - start_time

    return_code = process.close() or 0

    logging.debug(f"Output: {output}")

    # Validate the output with a regex, if specified
    if benchmark.get("output-validator") and not re.search(
        benchmark.get("output-validator"), output
    ):
        logging.warning(
            f"Output validation failed for benchmark {benchmark['name']} with runtime {runtime['name']}"
        )
        return 0, 0, return_code, output, {}
    logging.debug(
        f"Output validation succeeded for benchmark {benchmark['name']} with runtime {runtime['name']}"
    )

    score = (
        _parse_score(output, benchmark.get("score-parser"))
        if benchmark.get("score-parser")
        else 0
    )

    stats = {
        stat_name: match.group(stat_name)
        for stat_name, stat_regex in (runtime.get("stats-parser") or {}).items()
        if (match := re.search(stat_regex, output))
    }

    return elapsed_time, score, return_code, output, stats


def _compile_benchmark(benchmark, runtime, benchmarks_folder):
    """Compile a benchmark using AOT if applicable.

    Args:
        benchmark (dict): The benchmark to compile.
        runtime (dict): The runtime to use.
        benchmarks_folder (str): The folder containing the benchmarks.

    Returns:
        str: Path to the precompiled AOT file, or None if AOT is not applicable.
    """

    benchmarks_folder = utils.get_absolute_path(benchmarks_folder)

    benchmark_path = os.path.join(
        benchmarks_folder,
        benchmark["path"],
    )

    precompiled_path = os.path.splitext(benchmark_path)[0] + ".aot"

    if runtime["aot-command"]:
        aot_command = runtime["aot-command"].format(
            input=benchmark_path, output=precompiled_path
        )
        logging.debug(f"Running AOT command: '{aot_command}'")
        process = os.popen(aot_command)
        output = process.read()
        logging.debug(f"AOT output: {output}")
        if process.close() is not None:
            logging.error(
                f"AOT compilation failed for {benchmark['name']} with runtime {runtime['name']}"
            )
            return None

        logging.info(
            f"AOT compilation succeeded for {benchmark['name']} with runtime {runtime['name']}"
        )
        return precompiled_path

    return None


def _save_results_to_file(results, folder="results"):
    if not os.path.exists(folder):
        os.makedirs(folder)

    filename = os.path.join(folder, time.strftime("%Y-%m-%d_%H-%M-%S.json"))
    with open(filename, "w") as f:
        json.dump(results, f, indent=4)

    logging.info(f"Results saved to {filename}")


def main(args):
    logging.getLogger().setLevel(getattr(logging, args.log_level.upper()))

    args.benchmarks_folder = utils.get_absolute_path(args.benchmarks_folder)
    args.runtimes_file = utils.get_absolute_path(args.runtimes_file)
    args.results_folder = utils.get_absolute_path(args.results_folder)

    # Get the runtime objects from the command line arguments
    runtimes_list = runtimes.list_runtimes(file=args.runtimes_file)

    # "all" means subruntimes as well. we need to bring them to the top level.
    # Since we're at it, we'll also keep command and name only
    runtimes_list = [
        {
            "name": runtime["name"],
            "command": runtime["command"],
            "aot-command": runtime.get("aot-command", ""),
            "stats-parser": runtime.get("stats-parser", {}),
        }
        for runtime in runtimes_list
        for runtime in ([runtime] + runtime.pop("subruntimes", []))
    ]

    if "all" not in args.runtimes:
        runtimes_list = _filter_runtimes_by_name(args.runtimes, runtimes_list)

    # If path to the runtimes is not absolute, prepend the path to the runtimes folder
    for r in runtimes_list:
        if r["command"].strip() and not os.path.isabs(r["command"].strip()):
            r["command"] = os.path.join(
                os.path.dirname(os.path.abspath(args.runtimes_file)),
                r["command"],
            )

    for r in runtimes_list:
        if "aot-command" in r and r["aot-command"].strip():
            r["aot-command"] = (
                f"cd {os.path.dirname(os.path.abspath(args.runtimes_file))} && {r['aot-command']}"
            )

    logging.debug(f"Using runtimes: {[r['name'] for r in runtimes_list]}")

    # Get the benchmark objects from the command line arguments
    benchmarks_list = args.benchmarks
    if benchmarks_list == ["all"]:
        benchmarks_list = benchmarks.list_benchmarks(args.benchmarks_folder)
    else:
        benchmarks_list = _get_benchmarks_from_names(
            benchmarks_list, args.benchmarks_folder
        )

    logging.debug(f"Using benchmarks: {benchmarks_list}")

    # Run the benchmarks with the runtimes
    results = dict()

    for r in runtimes_list:
        logging.debug(f"Using runtime: {r['name']}")
        results[r["name"]] = dict()
        for b in _get_benchmarks(benchmarks_list):
            logging.info(f"Running benchmark: {b['name']} with runtime: {r['name']}")

            results[r["name"]][b["name"]] = []

            precompiled_path = None
            if r["aot-command"]:
                precompiled_path = _compile_benchmark(b, r, args.benchmarks_folder)

            for i in range(args.repeat):
                logging.info(f"Running iteration {i + 1}/{args.repeat}")
                elapsed_time, score, return_code, output, stats = (
                    _run_benchmark_with_runtime(
                        b, r, args.benchmarks_folder, precompiled_path
                    )
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

                logging.debug(f"Stats: {stats}")
                logging.debug(f"Storing output is disabled: {args.no_store_output}")

                # Output is stored unless the user specified not to
                results[r["name"]][b["name"]].append(
                    {
                        "elapsed_time": elapsed_time,
                        "score": score,
                        "return_code": return_code,
                        **({"output": output} if not args.no_store_output else {}),
                        **({"stats": stats} if stats else {}),
                    }
                )

            # Cleanup precompiled file after all iterations
            if precompiled_path and os.path.exists(precompiled_path):
                os.remove(precompiled_path)
                logging.debug(f"Removed precompiled file: {precompiled_path}")

    logging.debug(f"Results: {results}")

    _save_results_to_file(results, folder=args.results_folder)
