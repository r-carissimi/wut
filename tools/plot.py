"""Plots results of the benchmarks"""


def parse(parser):
    """Parse command-line arguments for the runtime module.

    Args:
        parser (ArgumentParser): The argument parser to add subcommands to.
    """

    parser.add_argument(
        "results_file",
        help="Path to the results file to plot",
        type=str,
    )

    parser.add_argument(
        "--plots-folder",
        default="plots",
        help="Path to the folder where plots will be saved (default: plots)",
    )

    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level (default: INFO)",
    )

    return parser


def main(args):
    print(f"Plotting results from {args.results_file}")
    print(f"Saving plots to {args.plots_folder}")
