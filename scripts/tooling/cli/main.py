import argparse
import sys


def main() -> None:
    parser = argparse.ArgumentParser(prog="tooling")
    subparsers = parser.add_subparsers(dest="group", metavar="GROUP")
    subparsers.required = True

    from scripts.tooling.cli.misc import register as _register_misc
    _register_misc(subparsers)

    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
