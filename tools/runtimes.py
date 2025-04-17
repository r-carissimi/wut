"""WebAssembly runtimes management

This module provides a command-line interface (CLI) for managing WebAssembly runtimes.
"""

import json
import logging
import os

from . import utils


def parse(parser):
    """Parse command-line arguments for the runtime module.

    Args:
        parser (ArgumentParser): The argument parser to add subcommands to.
    """

    subparsers = parser.add_subparsers(dest="operation", required=True)

    # "list" command to list installed runtimes
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

    # "available" command to list available runtimes
    available_parser = subparsers.add_parser(
        "available",
        help=_list_available_runtimes.__doc__.split("\n")[0],
        description=_list_available_runtimes.__doc__.split("\n")[0],
    )

    available_parser.add_argument(
        "--installers-folder",
        default="installers",
        help="Path to the folder containing installers (default: installers)",
    )

    # TODO: add "install" command to install a runtime

    # TODO: add "remove" command to remove a runtime

    for subparser in subparsers.choices.values():
        utils.add_log_level_argument(subparser)

    return parser


def _list_runtimes(file="runtimes/runtimes.json"):
    """List installed runtimes.

    Args:
        file (str): Path to the JSON file containing runtimes. File must
                    exist but can be empty.
                    Note that no runtime should be called "all" as that
                    is reserved for selecting all the runtimes.

    Returns:
        list: List of installed runtimes, defined as a list of dictionaries
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

    runtimes_list = _list_runtimes(file)
    for runtime in runtimes_list:
        if runtime["name"] == name:
            return runtime
    logging.warning(f"Runtime {name} not found.")
    return None


def _list_available_runtimes(installers_folder="installers"):
    """List available runtimes.

    Args:
        installers_folder (str): Path to the folder containing installer JSON files.

    Returns:
        list[dict]: List of available runtimes, each represented as a dictionary.
    """
    if not os.path.exists(installers_folder):
        logging.error(f"{installers_folder} folder not found.")
        return []
    if not os.path.isdir(installers_folder):
        logging.error(f"{installers_folder} is not a directory.")
        return []
    if os.listdir(installers_folder) == []:
        logging.warning(f"{installers_folder} is empty.")
        return []

    runtimes = []
    for entry in os.scandir(installers_folder):
        if entry.is_file() and entry.name.endswith(".json"):
            try:
                with open(entry.path, "r") as f:
                    runtime = json.load(f)
                    if not isinstance(runtime, dict) or "name" not in runtime:
                        logging.warning(
                            f"Invalid or missing 'name' in {entry.name}. Skipping."
                        )
                        continue
                    runtimes.append(runtime)
            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse {entry.name}: {e}")
            except Exception as e:
                logging.error(f"Unexpected error while processing {entry.name}: {e}")

    if not runtimes:
        logging.warning("No valid runtimes found in installers folder.")
        return []

    return runtimes


def main(args):
    logging.getLogger().setLevel(getattr(logging, args.log_level.upper()))
    if args.operation == "list":
        runtimes_list = _list_runtimes(args.runtimes_file)
        if not runtimes_list:
            print("No runtimes found.")
            return

        print("Runtimes installed:")
        for runtime in runtimes_list:
            logging.debug(f"Found runtime: {runtime}")
            print(f" * {runtime['name']}: {runtime['desc']}")

    elif args.operation == "available":
        available_runtimes = _list_available_runtimes(args.installers_folder)
        if not available_runtimes:
            print("No runtimes found.")
            return
        print("Available runtimes:")
        for runtime in available_runtimes:
            print(f" * {runtime['name']}: {runtime['desc']}")

    else:
        print("Unknown operation. Use 'list' to see available runtimes.")
