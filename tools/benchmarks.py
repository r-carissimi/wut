"""Manages installed benchmarks

This module provides a command-line interface (CLI) for managing WebAssembly benchmarks.
"""

import json
import logging
import os

from . import utils


def parse(parser):
    """Parse command-line arguments for the benchmarks module.

    Args:
        parser (ArgumentParser): The argument parser to add subcommands to.
    """

    # We use os.path.dirname two times because the script is in the tools
    # folder and we want to get the runtimes folder.
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    subparsers = parser.add_subparsers(dest="operation", required=True)
    list_parser = subparsers.add_parser(
        "list",
        help=list_benchmarks.__doc__.split("\n")[0],
        description=list_benchmarks.__doc__.split("\n")[0],
    )

    list_parser.add_argument(
        "--benchmarks-folder",
        default=os.path.join(script_dir, utils.DEFAULT_BENCHMARKS_FOLDER),
        help=f"Path to the folder containing benchmarks (default: {utils.DEFAULT_BENCHMARKS_FOLDER}).",
    )

    for subparser in subparsers.choices.values():
        utils.add_log_level_argument(subparser)

    return parser


def _parse_benchmark_json(file):
    """Parse a JSON file containing benchmark information.

    Args:
        file (str): Path to the JSON file containing benchmark information.
                    File must exist but can be empty.

                    Example:
                    {
                        "benchmarks": [
                            {
                                "name": "benchmark1",
                                "path": "path/to/benchmark1"
                            },
                            {
                                "name": "benchmark2",
                                "path": "path/to/benchmark2"
                            }
                        ]
                    }
    Returns:
        list: List of benchmarks, defined as a list of dictionaries
              containing benchmark information. List is empty if no benchmarks
              are found.
              Example:
                [
                    {
                        "name": "benchmark1",
                        "path": "path/to/benchmark1"
                    },
                    {
                        "name": "benchmark2",
                        "path": "path/to/benchmark2"
                    }
                ]
    """

    if os.path.getsize(file) == 0:
        logging.info(f"{file} is empty. Skipping.")
        return []

    try:
        with open(file, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        logging.info(f"Failed to parse JSON in {file}: {e}")
        return []

    benchmarks = data.get("benchmarks", [])
    if not benchmarks:
        logging.info(f"No benchmarks found in {file}. Skipping.")
        return []

    return [
        benchmark
        for benchmark in benchmarks
        if "name" in benchmark and "path" in benchmark
    ]


def list_groups(folder=utils.DEFAULT_BENCHMARKS_FOLDER):
    """List all groups in the benchmarks folder.

    Args:
        folder (str): Path to the folder containing benchmarks. Folder must
                      exist but can be empty. Note that no group should be called
                      "all" as this is reserved for selecting all benchmarks.
                      The group will not be able to be used.

    Returns:
        list: List of benchmark groups, defined as all subfolders in the
              benchmarks folder that contain a "benchmarks.json" file.
              List is empty if no subfolders are found.
    """

    if not os.path.exists(folder):
        logging.error(f"{folder} folder not found.")
        return []
    if not os.path.isdir(folder):
        logging.error(f"{folder} is not a directory.")
        return []

    groups = [
        f
        for f in os.listdir(folder)
        if os.path.exists(os.path.join(folder, f, "benchmarks.json"))
    ]

    return groups


def list_benchmarks(folder=utils.DEFAULT_BENCHMARKS_FOLDER):
    """List available benchmarks.

    Args:
        folder (str): Path to the folder containing benchmarks. Folder must
                      exist but can be empty.

    Returns:
        dict: Dictionary of benchmark groups, where each key is a group name
              and the value is a list of benchmarks in that group.

              Example:
                {
                    "group1": [
                        {
                            "name": "benchmark1",
                            "path": "path/to/benchmark1"
                        },
                        {
                            "name": "benchmark2",
                            "path": "path/to/benchmark2"
                        }
                    ],
                    "group2": [
                        {
                            "name": "benchmark3",
                            "path": "path/to/benchmark3"
                        }
                    ]
                }
    """

    benchmarks = {
        group: _parse_benchmark_json(os.path.join(folder, group, "benchmarks.json"))
        for group in list_groups(folder)
        if _parse_benchmark_json(os.path.join(folder, group, "benchmarks.json"))
    }

    return benchmarks


def get_benchmark_from_name(name, folder=utils.DEFAULT_BENCHMARKS_FOLDER):
    """Get benchmark information from a name.
    Args:
        name (str): Name of the benchmark. Can be a group name or a
                    group/benchmark name.
                    Example: "coremark" or "coremark/coremark-1000"
    Returns:
        dict: Dictionary containing benchmark information. Returns None if
              the benchmark is not found. A single benchmark is returned in a
              list with the name of its group.

              Example:
                {
                "coremark": [
                        {
                            "name": "coremark-1000",
                            "path": "coremark-1000.wasm"
                        }
                    ]
                }
    """
    if not name:
        return None

    benchmarks = list_benchmarks(folder)

    if "/" not in name:
        return {name: benchmarks.get(name)} if name in benchmarks else None

    group, _, benchmark = name.partition("/")
    if group not in benchmarks:
        logging.warning(f"Benchmark group {group} not found.")
        return None

    benchmark_info = next(
        (b for b in benchmarks[group] if b["name"] == benchmark), None
    )
    if benchmark_info:
        return {group: [benchmark_info]}

    logging.warning(f"Benchmark {benchmark} not found in group {group}.")
    return None


def main(args):
    logging.getLogger().setLevel(getattr(logging, args.log_level.upper()))

    args.benchmarks_folder = utils.get_absolute_path(args.benchmarks_folder)

    if args.operation == "list":
        benchmarks = list_benchmarks(args.benchmarks_folder)

        if not benchmarks:
            logging.warning("No benchmarks found.")
            print("No benchmarks found.")
            return

        print("Available benchmarks:")
        for group in benchmarks:
            print(f" * {group}:")
            for benchmark in benchmarks[group]:
                print(f"   ↳ {benchmark['name']}")
    else:
        print("Unknown operation. Use 'list' to see available runtimes.")
