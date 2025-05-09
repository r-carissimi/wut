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
        "--runtimes-folder",
        default="runtimes",
        help="Path to the folder containing runtimes (default: runtimes)",
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


def _get_named_benchmarks(benchmarks_list, benchmarks_folder="benchmarks"):
    benchs = dict()

    for benchmark_name in benchmarks_list:
        # Ignore benchmarks specified as files as they have already been loaded
        if benchmark_name.endswith(".wasm"):
            continue
        b = benchmarks.get_benchmark_from_name(benchmark_name, benchmarks_folder)
        if b is not None:
            for k, v in b.items():
                # This creates a new list if the key does not exist
                # and append the benchmark to the list. This is done to support
                # specifying single benchmarks in a group.
                benchs.setdefault(k, []).extend(v)

    return benchs


def _load_benchmarks(benchmarks_list, benchmarks_folder):
    """Load benchmarks from a list of names and files.

    Args:
        benchmarks (list): List of benchmark names or file paths.
        benchmarks_folder (str): Path to the folder containing benchmark definitions.

    Returns:
        list: A list of benchmark dictionaries with their names and paths.
    """

    # Load benchmarks from files
    file_benchmarks = [
        {"name": os.path.basename(b), "path": os.path.abspath(b)}
        for b in benchmarks_list
        if b.endswith(".wasm") and os.path.isfile(b)
    ]

    logging.debug(f"File benchmarks: {file_benchmarks}")

    # Load benchmarks from benchmark groups
    named_benchmarks = (
        benchmarks.list_benchmarks(benchmarks_folder)
        if "all" in benchmarks_list
        else _get_named_benchmarks(benchmarks_list, benchmarks_folder)
    )

    return _flatten_benchmarks(named_benchmarks) + file_benchmarks


def _flatten_benchmarks(benchmarks_list):
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
    benchmark, runtime, benchmarks_folder, runtimes_folder, precompiled_path=None
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
               * stats: A dictionary containing the parsed stats from the output
    """

    benchmarks_folder = utils.get_absolute_path(benchmarks_folder)

    benchmark_path = os.path.join(
        benchmarks_folder,
        benchmark["path"],
    )

    if precompiled_path:
        benchmark_path = precompiled_path

    # Replaces the path in the arguments with the absolute path to the benchmark
    # folder. This is due to some runtimes that do not support mapping
    # directories to a different path in the WASM module. Hence, we need to
    # provide the absolute path to the benchmark folder for the file to be
    # accessible.
    arguments = benchmark.get("args", "").format(path=os.path.dirname(benchmark_path))

    # Command formatting
    command = runtime["command"].format(
        payload=f'"{benchmark_path}"',
        entrypoint=benchmark.get("entrypoint", "")
        if "{entrypoint}" in runtime["command"]
        else "",
        entrypoint_flag=runtime["entrypoint-flag"]
        if "{entrypoint_flag}" in runtime["command"] and "entrypoint" in benchmark
        else "",
        args=arguments if "{args}" in runtime["command"] else "",
        mount_dir=f'"{os.path.dirname(benchmark_path)}"'
        if "{mount_dir}" in runtime["command"]
        else "",
    )

    logging.debug(f"Running '{command}'")

    os.chdir(runtimes_folder)

    start_time = time.perf_counter_ns()
    process = os.popen(command)
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


def _compile_benchmark(benchmark, runtime, benchmarks_folder, runtimes_folder):
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
            input=f'"{benchmark_path}"', output=f'"{precompiled_path}"'
        )
        logging.debug(f"Running AOT command: '{aot_command}'")
        os.chdir(runtimes_folder)
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


def _get_runtimes(runtimes_file, chosen_runtimes):
    """Loads and prepares the list of runtimes."""

    runtimes_list = runtimes.list_runtimes(file=runtimes_file)
    flattened_runtimes = [
        runtime
        for runtime in runtimes_list
        for runtime in ([runtime] + runtime.pop("subruntimes", []))
    ]

    if "all" in chosen_runtimes:
        return flattened_runtimes

    return _filter_runtimes_by_name(chosen_runtimes, flattened_runtimes)


def _run_benchmarks(
    runtimes_list,
    benchmarks_list,
    benchmarks_folder,
    runtimes_folder,
    repeat=1,
    no_store_output=False,
):
    """Runs benchmarks for each runtime and collects results."""

    results = {}

    for runtime in runtimes_list:
        logging.debug(f"Using runtime: {runtime['name']}")
        results[runtime["name"]] = {}

        for benchmark in benchmarks_list:
            logging.info(
                f"Running benchmark: {benchmark['name']} with runtime: {runtime['name']}"
            )
            results[runtime["name"]][benchmark["name"]] = run_benchmark_iterations(
                benchmark,
                runtime,
                benchmarks_folder,
                runtimes_folder,
                repeat,
                no_store_output,
            )

    return results


def run_benchmark_iterations(
    benchmark,
    runtime,
    benchmarks_folder,
    runtimes_folder,
    repeat=1,
    no_store_output=False,
):
    """Runs multiple iterations of a benchmark and collects results.

    Args:
        benchmark (dict): The benchmark to run.
        runtime (dict): The runtime to use.
        benchmarks_folder (str): The folder containing the benchmarks.
        runtimes_folder (str): The folder containing the runtimes.
        repeat (int): Number of times to repeat the benchmark.
        no_store_output (bool): If True, do not store the output of the benchmark.

    Returns:
        list: A list of dictionaries containing the results of each iteration.
        Returns None if the benchmark fails to compile.
    """

    iterations_results = []
    precompiled_path = None

    if runtime.get("aot-command"):
        precompiled_path = _compile_benchmark(
            benchmark, runtime, benchmarks_folder, runtimes_folder
        )
        if precompiled_path is None:
            return None

    for i in range(repeat):
        logging.info(f"Running iteration {i + 1}/{repeat}")
        elapsed_time, score, return_code, output, stats = _run_benchmark_with_runtime(
            benchmark,
            runtime,
            benchmarks_folder,
            runtimes_folder,
            precompiled_path,
        )

        if return_code != 0:
            logging.warning(
                f"Benchmark {benchmark['name']} failed with return code {return_code}"
            )
            elapsed_time, score = 0, 0

        iterations_results.append(
            {
                "elapsed_time": elapsed_time,
                "score": score,
                "return_code": return_code,
                **({"output": output} if not no_store_output else {}),
                **({"stats": stats} if stats else {}),
            }
        )

    if precompiled_path and os.path.exists(precompiled_path):
        os.remove(precompiled_path)
        logging.debug(f"Removed precompiled file: {precompiled_path}")

    return iterations_results


def main(args):
    logging.getLogger().setLevel(getattr(logging, args.log_level.upper()))

    # Resolve absolute paths for key arguments
    benchmarks_folder = utils.get_absolute_path(args.benchmarks_folder)
    runtimes_file = utils.get_absolute_path(args.runtimes_file)
    results_folder = utils.get_absolute_path(args.results_folder)
    runtimes_folder = utils.get_absolute_path(args.runtimes_folder)

    # Loads the runtimes
    runtimes_list = _get_runtimes(runtimes_file, args.runtimes)
    logging.debug(f"Using runtimes: {[r['name'] for r in runtimes_list]}")

    # Load the benchmarks from the command line arguments
    benchmarks_list = _load_benchmarks(args.benchmarks, benchmarks_folder)
    logging.debug(f"Using benchmarks: {benchmarks_list}")

    if not benchmarks_list:
        logging.error("No benchmarks found. Exiting.")
        return

    # Run benchmarks
    results = _run_benchmarks(
        runtimes_list,
        benchmarks_list,
        benchmarks_folder,
        runtimes_folder,
        args.repeat,
        args.no_store_output,
    )

    # Save results
    _save_results_to_file(results, folder=results_folder)
