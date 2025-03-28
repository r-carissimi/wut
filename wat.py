import logging
from argparse import ArgumentParser

from tools import commands

VERSION = "0.1α (2025-03-28)"


def setup_subparsers(parser, commands):
    """Set up subparsers for the given commands."""
    subparser = parser.add_subparsers(dest="command", required=True)
    for name, command in commands.items():
        cmd_parser = subparser.add_parser(
            name,
            help=command.__doc__.split("\n")[0],
            description=command.__doc__.split("\n")[0],
            add_help=True,
        )
        command._parse(cmd_parser)
        cmd_parser.set_defaults(_func=command._main)


def setup_logging(level=logging.WARNING):
    """Set up logging configuration."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def main():
    parser = ArgumentParser(description="WAT - WAT Analyzes Timing")
    parser.add_argument("--version", action="version", version=f"WAT {VERSION}")
    parser.add_argument(
        "--log-level",
        default="WARNING",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level (default: WARNING)",
    )
    setup_subparsers(parser, commands)

    args = parser.parse_args()
    setup_logging(level=getattr(logging, args.log_level.upper()))

    if hasattr(args, "_func"):
        args._func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
