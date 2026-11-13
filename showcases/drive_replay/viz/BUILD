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
load("@rules_python//python:defs.bzl", "py_library")
load("@score_tooling//python_basics:defs.bzl", "score_py_pytest")

# Runs on the laptop with foxglove-websocket from requirements.txt; the test stubs that dependency.
py_library(
    name = "foxglove_bridge",
    srcs = ["foxglove_bridge.py"],
)

score_py_pytest(
    name = "foxglove_bridge_test",
    srcs = ["foxglove_bridge_test.py"],
    pytest_config = "//:pyproject.toml",
    deps = [":foxglove_bridge"],
)
