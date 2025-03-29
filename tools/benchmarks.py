"""Webassembly benchmarks management

This module provides a command-line interface (CLI) for managing WebAssembly benchmarks."""

import json
import logging
import os


def parse(parser):
    """Parse command-line arguments for the benchmarks module.

    Args:
        parser (ArgumentParser): The argument parser to add subcommands to.
    """

    subparsers = parser.add_subparsers(dest="operation", required=True)
    list_parser = subparsers.add_parser(
        "list",
        help=list_benchmarks.__doc__.split("\n")[0],
        description=list_benchmarks.__doc__.split("\n")[0],
    )

    list_parser.add_argument(
        "--benchmarks-folder",
        default="benchmarks",
        help="Path to the folder containing benchmarks (default: benchmarks)",
    )

    for subparser in subparsers.choices.values():
        subparser.add_argument(
            "--log-level",
            default="WARNING",
            choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            help="Set the logging level (default: WARNING)",
        )

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
    Raises:
        FileNotFoundError: If the specified file does not exist.
        NotADirectoryError: If the specified path is not a directory.
    """

    if os.path.getsize(os.path.join(file)) == 0:
        logging.info(f"{file} is empty. Skipping.")
        return list()

    benchmarks = []

    with open(file, "r") as f:
        try:
            benchmarks_list = json.load(f)
            if not benchmarks_list or "benchmarks" not in benchmarks_list:
                logging.info(f"No benchmarks found in {file}. Skipping.")
                return []

            benchmarks_list = benchmarks_list["benchmarks"]
            for benchmark in benchmarks_list:
                if "name" not in benchmark or "path" not in benchmark:
                    logging.info(f"Invalid benchmark format in {file}. Skipping.")
                    continue

                benchmarks.append(benchmark)
        except json.JSONDecodeError as e:
            logging.info(f"Failed to parse JSON in {file}: {e}")

    return benchmarks


def list_groups(folder="benchmarks"):
    """List all groups in the benchmarks folder.

    Args:
        folder (str): Path to the folder containing benchmarks. Folder must
                      exist but can be empty.

    Returns:
        list: List of benchmark groups, defined as all subfolders in the
              benchmarks folder that contain a "benchmarks.json" file.
              List is empty if no subfolders are found.

    Raises:
        FileNotFoundError: If the specified folder does not exist.
        NotADirectoryError: If the specified path is not a directory.
    """

    if not os.path.exists(folder):
        logging.error(f"{folder} folder not found.")
        raise FileNotFoundError(f"{folder} folder not found.")
    if not os.path.isdir(folder):
        logging.error(f"{folder} is not a directory.")
        raise NotADirectoryError(f"{folder} is not a directory.")

    groups = [
        f
        for f in os.listdir(folder)
        if os.path.exists(os.path.join(folder, f, "benchmarks.json"))
    ]

    return groups


def list_benchmarks(folder="benchmarks"):
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

    Raises:
        FileNotFoundError: If the specified folder does not exist.
        NotADirectoryError: If the specified path is not a directory.
    """

    groups = list_groups(folder)

    benchmarks = dict()

    for group in groups:
        logging.debug(f"Found benchmark group: {group}")
        file = os.path.join(folder, group, "benchmarks.json")
        list_benchmarks = _parse_benchmark_json(file)
        if not list_benchmarks:
            logging.info(f"No benchmarks found in {file}. Skipping.")
            continue
        benchmarks[group] = list_benchmarks
        logging.debug(f"Found benchmarks: {benchmarks[group]}")

    return benchmarks


def main(args):
    logging.getLogger().setLevel(getattr(logging, args.log_level.upper()))
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
