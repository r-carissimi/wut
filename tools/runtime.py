"""WebAssembly runtime management

This module provides a command-line interface (CLI) for managing WebAssembly runtimes.
"""

import json
import logging
import os


def parse(parser):
    """Parse command-line arguments for the runtime module.

    Args:
        parser (ArgumentParser): The argument parser to add subcommands to.
    """

    subparsers = parser.add_subparsers(dest="operation", required=True)
    list_parser = subparsers.add_parser(
        "list",
        help=_list_runtimes.__doc__.split("\n")[0],
        description=_list_runtimes.__doc__.split("\n")[0],
    )

    list_parser.add_argument(
        "--runtimes-file",
        default="runtimes/runtimes.json",
        help="Path to the JSON file containing runtimes (default: runtimes/runtimes.json)",
    )

    for subparser in subparsers.choices.values():
        subparser.add_argument(
            "--log-level",
            default="WARNING",
            choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            help="Set the logging level (default: WARNING)",
        )

    return parser


def _list_runtimes(file="runtimes/runtimes.json"):
    """List available runtimes.

    Args:
        file (str): Path to the JSON file containing runtimes.
    """

    if not os.path.exists(file):
        logging.error(f"{file} file not found.")
        return
    if os.path.getsize(file) == 0:
        logging.warning(f"{file} is empty.")
        print("No runtimes found.")
        return

    with open(file, "r") as f:
        try:
            runtime_list = json.load(f)
            if not runtime_list or "runtimes" not in runtime_list:
                logging.warning("No runtimes found in runtimes.json.")
                print("No runtimes found.")
                return
            print("Runtimes available:")
            for runtime in runtime_list["runtimes"]:
                logging.debug(f"Found runtime: {runtime}")
                print(f"  - {runtime['name']}: {runtime['desc']}")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return


def main(args):
    logging.getLogger().setLevel(getattr(logging, args.log_level.upper()))
    if args.operation == "list":
        _list_runtimes(args.runtimes_file)
    else:
        print("Unknown operation. Use 'list' to see available runtimes.")
