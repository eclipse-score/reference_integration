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
    """Register workflow utility commands."""
    workflow_parser = subparsers.add_parser("workflow", help="Workflow utility commands")
    workflow_sub = workflow_parser.add_subparsers(dest="command", metavar="COMMAND")
    workflow_sub.required = True

    from scripts.tooling.cli.workflow.extract_codeql_metrics import (
        register as _register_extract_codeql_metrics,
    )

    _register_extract_codeql_metrics(workflow_sub)

