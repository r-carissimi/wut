from argparse import ArgumentParser

from tools import commands

VERSION = "0.1α (2025-03-28)"


def setup_subparsers(parser, commands):
    """Set up subparsers for the given commands."""
    subparser = parser.add_subparsers(dest="command", required=True)
    for name, command in commands.items():
        cmd_parser = subparser.add_parser(
            name, help=command.__desc, description=command.__desc
        )
        command._parse(cmd_parser)
        cmd_parser.set_defaults(_func=command._main)


def main():
    parser = ArgumentParser(description="WAT - WAT Analyzes Timing")
    parser.add_argument("--version", action="version", version=f"WAT {VERSION}")
    setup_subparsers(parser, commands)

    args = parser.parse_args()
    if hasattr(args, "_func"):
        args._func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
