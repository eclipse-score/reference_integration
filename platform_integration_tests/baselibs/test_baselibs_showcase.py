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
import re

from attribute_plugin import add_test_properties
from showcase_runner import run_showcases

_LEVELS = ("info", "warn", "error", "fatal")


def _assert_logged(output: str, context: str, message: str) -> None:
    """StdoutLogger line format: ``[...][<pid>][<context>][<LEVEL>] <message>``."""
    pattern = rf"\[{re.escape(context)}\]\[[^\]]+\] {re.escape(message)}\s*$"
    assert re.search(pattern, output, re.MULTILINE), f"No '{message}' logged with context '{context}':\n{output}"


@add_test_properties(
    partially_verifies=["feat_req__baselibs__utils_library"],
    test_type="interface-test",
    derivation_technique="requirements-analysis",
)
def test_baselibs_builtin_logger_showcase(target):
    """The built-in stdout logger emits Info and above for both the default
    and an overridden context, and filters Trace/Debug."""
    output = run_showcases(target, "Baselibs Builtin Logger Example")
    for context in ("EXAMPLE", "CHANGED"):
        for level in _LEVELS:
            _assert_logged(output, context, f"{level} log")
    assert "hidden" not in output, f"Trace/Debug messages were not filtered:\n{output}"


@add_test_properties(
    partially_verifies=["feat_req__baselibs__utils_library"],
    test_type="interface-test",
    derivation_technique="requirements-analysis",
)
def test_baselibs_custom_logger_showcase(target):
    """A custom global logger receives Info and above and filters Trace/Debug."""
    run_showcases(target, "Baselibs Custom Logger Example")

    # The custom logger writes to stderr, which the QEMU target does not
    # capture, so re-run the app with stderr merged to check its output.
    exit_code, out = target.execute("/showcases/bin/log_custom 2>&1")
    output = out.decode(errors="replace")
    assert exit_code == 0, f"log_custom exited with {exit_code}:\n{output}"
    for level in _LEVELS:
        assert f"{level} log" in output, f"'{level} log' missing:\n{output}"
    assert "hidden" not in output, f"Trace/Debug messages were not filtered:\n{output}"


@add_test_properties(
    partially_verifies=["feat_req__baselibs__multi_language_apis"],
    test_type="interface-test",
    derivation_technique="requirements-analysis",
)
def test_baselibs_cpp_logger_init_showcase(target):
    """A logger configured from C++ is used by Rust code, for the C++-set
    default context and for explicit contexts."""
    output = run_showcases(target, "Baselibs C++ Logger Init Example")
    for context in ("ABCD", "EX1", "EX2"):
        _assert_logged(output, context, "This is an info log")
    _assert_logged(output, "ABCD", "This is a fatal log")
