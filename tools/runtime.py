"""WebAssembly runtimes management

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
        help=list_runtimes.__doc__.split("\n")[0],
        description=list_runtimes.__doc__.split("\n")[0],
    )

    list_parser.add_argument(
        "--runtimes-file",
        default="runtimes/runtimes.json",
        help="Path to the JSON file containing runtimes (default: runtimes/runtimes.json)",
    )

    for subparser in subparsers.choices.values():
        subparser.add_argument(
            "--log-level",
            default="INFO",
            choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            help="Set the logging level (default: INFO)",
        )

    return parser


def list_runtimes(file="runtimes/runtimes.json"):
    """List available runtimes.

    Args:
        file (str): Path to the JSON file containing runtimes. File must
                    exist but can be empty.
                    Note that no runtime should be called "all" as that
                    is reserved for selecting all the runtimes.

    Returns:
        list: List of available runtimes, defined as a list of dictionaries
              containing runtime information. List is empty if no runtimes
              are found.

              Example:
                [
                    {
                        "name": "wasmtime",
                        "desc": "A standalone WebAssembly runtime",
                        "command": "/usr/bin/wasmtime",
                    },
                    {
                        "name": "wasmer",
                        "desc": "A WebAssembly runtime for embedding in other languages",
                        "command": "/usr/bin/wasmer",
                    }
                ]

    Raises:
        FileNotFoundError: If the specified file does not exist.
        json.JSONDecodeError: If the JSON file is malformed.
        KeyError: If the JSON file does not contain the expected structure.
    """

    if not os.path.exists(file):
        logging.error(f"{file} file not found.")
        raise FileNotFoundError(f"{file} file not found.")
    if os.path.getsize(file) == 0:
        logging.warning(f"{file} is empty.")
        return list()

    with open(file, "r") as f:
        runtime_list = json.load(f)
        if not runtime_list or "runtimes" not in runtime_list:
            logging.warning("No runtimes found in runtimes.json.")
            return list()

        return runtime_list["runtimes"]


def get_runtime_from_name(name, file="runtimes/runtimes.json"):
    """Get runtime information from a name.

    Args:
        name (str): Name of the runtime.

    Returns:
        dict: Dictionary containing runtime information. Returns None if
              the runtime is not found.
              Example:
                {
                    "name": "wasmtime",
                    "desc": "A standalone WebAssembly runtime",
                    "command": "/usr/bin/wasmtime"
                }
    """

    runtimes_list = list_runtimes(file)
    for runtime in runtimes_list:
        if runtime["name"] == name:
            return runtime
    logging.warning(f"Runtime {name} not found.")
    return None


def main(args):
    logging.getLogger().setLevel(getattr(logging, args.log_level.upper()))
    if args.operation == "list":
        runtimes_list = list_runtimes(args.runtimes_file)
        if not runtimes_list:
            print("No runtimes found.")
            return

        print("Runtimes available:")
        for runtime in runtimes_list:
            logging.debug(f"Found runtime: {runtime}")
            print(f" * {runtime['name']}: {runtime['desc']}")

    else:
        print("Unknown operation. Use 'list' to see available runtimes.")
