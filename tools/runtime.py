"""WebAssembly runtime management."""

import json


def _parse(parser):
    subparsers = parser.add_subparsers(dest="operation", required=True)
    subparsers.add_parser("list", help="List available runtimes")
    return parser


def _list_runtimes():
    print("Runtimes available:")
    with open("runtimes/runtimes.json", "r") as f:
        runtime_list = json.load(f)
        for runtime in runtime_list["runtimes"]:
            print(f"  - {runtime['name']}: {runtime['desc']}")


def _main(args):
    if args.operation == "list":
        _list_runtimes()
    else:
        print("Unknown operation. Use 'list' to see available runtimes.")
