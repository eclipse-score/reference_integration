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


def register(subparsers: argparse._SubParsersAction) -> None:
    release_parser = subparsers.add_parser("release", help="Release utilities")
    release_sub = release_parser.add_subparsers(dest="command", metavar="COMMAND")
    release_sub.required = True

    from scripts.tooling.cli.release.check_approvals import (
        register as _register_release_approvals,
    )

    _register_release_approvals(release_sub)
