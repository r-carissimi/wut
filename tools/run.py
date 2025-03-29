"""Runs benchmarks using runtimes"""

import logging
import os

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
        "--log-level",
        default="WARNING",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level (default: WARNING)",
    )

    return parser


def _get_runtimes_from_names(runtimes_list):
    runtimes = []
    for runtime_name in runtimes_list:
        if runtime_name == "all":
            continue

        r = runtime.get_runtime_from_name(runtime_name)
        if r is not None:
            runtimes.append(r)

    return runtimes


def _get_runtime_paths(runtimes_list):
    return [r["command"] for r in runtimes_list]


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


def _get_benchmarks_paths(benchmarks_list):
    paths = list()

    for group, b in benchmarks_list.items():
        paths.extend([os.path.join(group, benchmark["path"]) for benchmark in b])

    return paths


def main(args):
    logging.getLogger().setLevel(getattr(logging, args.log_level.upper()))

    runtimes_list = args.runtimes
    if runtimes_list == ["all"]:
        runtimes_list = runtime.list_runtimes()
    else:
        runtimes_list = _get_runtimes_from_names(runtimes_list)

    logging.debug(f"Using runtimes: {[r['name'] for r in runtimes_list]}")

    benchmarks_list = args.benchmarks
    if benchmarks_list == ["all"]:
        benchmarks_list = benchmarks.list_benchmarks()
    else:
        benchmarks_list = _get_benchmarks_from_names(benchmarks_list)

    logging.debug(f"Using benchmarks: {benchmarks_list}")

    for r in _get_runtime_paths(runtimes_list):
        logging.debug(f"Using runtime: {r}")
        for b in _get_benchmarks_paths(benchmarks_list):
            # TODO actually run the benchmark

            logging.info(f"Running benchmark: {b} with runtime: {r}")
