import argparse


def register(subparsers: argparse._SubParsersAction) -> None:
    misc_parser = subparsers.add_parser("misc", help="Miscellaneous utilities")
    misc_sub = misc_parser.add_subparsers(dest="command", metavar="COMMAND")
    misc_sub.required = True

    from scripts.tooling.cli.misc.html_report import register as _register_html_report

    _register_html_report(misc_sub)
