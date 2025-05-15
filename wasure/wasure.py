import logging
from argparse import ArgumentParser

from wasure.tools import commands, utils

VERSION_NUMBER = "0.7"
VERSION = f"{VERSION_NUMBER}α (2025-05-15)"


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
        command.parse(cmd_parser)
        cmd_parser.set_defaults(_func=command.main)


def setup_logging(level=logging.WARNING):
    """Set up logging configuration."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def main():
    parser = ArgumentParser(
        description="WASURE - WebAssembly SUite for Runtime Evaluation"
    )
    parser.add_argument("--version", action="version", version=f"WASURE {VERSION}")
    utils.add_log_level_argument(parser)
    setup_subparsers(parser, commands)

    args = parser.parse_args()
    setup_logging(level=getattr(logging, args.log_level.upper()))

    if hasattr(args, "_func"):
        args._func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
