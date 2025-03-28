"""Webassembly benchmarks management"""

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
        help=_list_benchmarks.__doc__.split("\n")[0],
        description=_list_benchmarks.__doc__.split("\n")[0],
    )

    list_parser.add_argument(
        "--folder",
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


def _list_benchmarks(folder="benchmarks"):
    """List available benchmarks.

    Args:
                folder (str): Path to the folder containing benchmarks.
    """

    if not os.path.exists(folder):
        logging.error(f"{folder} folder not found.")
        return
    if not os.path.isdir(folder):
        logging.error(f"{folder} is not a directory.")
        return

    # Recursive search for .wasm files
    benchmarks = []
    for root, _, files in os.walk(folder):
        benchmarks.extend(
            os.path.relpath(os.path.join(root, f), folder)
            for f in files
            if f.endswith(".wasm")
        )

    if not benchmarks:
        logging.warning("No benchmarks found.")
        print("No benchmarks found.")
        return

    print("Available benchmarks:")
    for benchmark in benchmarks:
        print(f"  - {benchmark}")


def main(args):
    logging.getLogger().setLevel(getattr(logging, args.log_level.upper()))
    if args.operation == "list":
        _list_benchmarks(args.folder)
    else:
        print("Unknown operation. Use 'list' to see available runtimes.")
