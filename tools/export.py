"""Exports results to a CSV file."""

import logging
import os

from . import utils


def parse(parser):
    """Parse command-line arguments for the runtime module."""
    parser.add_argument(
        "results_file",
        help="Path to the results file to plot",
        type=str,
    )

    parser.add_argument(
        "--csv-folder",
        default="results",
        help="Path to the folder where CSVs will be saved (default: results)",
    )

    utils.add_log_level_argument(parser)

    return parser


def main(args):
    logging.getLogger().setLevel(getattr(logging, args.log_level.upper()))
    os.makedirs(args.csv_folder, exist_ok=True)


# TODO: make the actual export. Probably can reuse most of the
# code from the plot module. Think about how to do it.
# Maybe create a "utils" module.
