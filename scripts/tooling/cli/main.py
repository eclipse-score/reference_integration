# *******************************************************************************
# Copyright (c) 2026 Contributors to the Eclipse Foundation
#
# See the NOTICE file(s) distributed with this work for additional
# information regarding copyright ownership.
#
# This program and the accompanying materials are made available under the
# terms of the Apache License Version 2.0 which is available at
# https://www.apache.org/licenses/LICENSE-2.0
#
# SPDX-License-Identifier: Apache-2.0
# *******************************************************************************
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
