"""Webassembly benchmarks management

This module provides a command-line interface (CLI) for managing WebAssembly benchmarks."""

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


def list_benchmarks(folder="benchmarks"):
    """List available benchmarks.

    Args:
        folder (str): Path to the folder containing benchmarks. Folder must
                      exist but can be empty.

    Returns:
        list: List of available benchmarks, defined as all .wasm files in
              the folder and its subfolders. list is empty if no .wasm files
              are found.

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

    # Recursive search for .wasm files
    benchmarks = []
    for root, _, files in os.walk(folder):
        benchmarks.extend(
            os.path.relpath(os.path.join(root, f), folder)
            for f in files
            if f.endswith(".wasm")
        )

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
        for benchmark in list_benchmarks(args.benchmarks_folder):
            print(f"  - {benchmark}")
    else:
        print("Unknown operation. Use 'list' to see available runtimes.")
