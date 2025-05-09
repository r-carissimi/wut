import json
import logging
import os


def add_log_level_argument(parser):
    """Add a --log-level argument to the parser."""

    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Set the logging level (default: INFO)",
    )

    return parser


def load_results_file(file_path):
    """Load benchmark results from a JSON file.

    Args:
        file_path (str): Path to the JSON file containing benchmark results.

    Returns:
        dict: Parsed benchmark results. If the file is empty or cannot be parsed,
              returns None.
    """
    try:
        with open(file_path, "r") as f:
            results = json.load(f)
            if not results:
                logging.info("No results found in the file.")
                return None
            return results
    except json.JSONDecodeError:
        logging.error("Failed to decode JSON from the results file.")
        return None


def get_absolute_path(path):
    """Get the absolute path of a given path. The path can be relative or absolute.
    If the path is relative, it has to be relative to the project root.
    The function assumes to be called from a script in the "tools" folder.

    Args:
        path (str): The path to convert to an absolute path.

    Returns:
        str: The absolute path.
    """

    # We use os.path.dirname two times because the script is in the tools
    # folder and we want to get the runtimes folder.

    if not os.path.isabs(path):
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(script_dir, path)

    return path
