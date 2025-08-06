# *******************************************************************************
# Copyright (c) 2025 Contributors to the Eclipse Foundation
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
# load("//:defs.bzl", "py_itf_test")
load("@score_itf//bazel:py_itf_test.bzl", "py_itf_test")

# py_itf_test = local_py_itf_test

py_itf_test(
    name = "fit_example_test",
    srcs = glob(["tests/**/*.py"]) + ["conftest.py"],
    args = [
        "--docker-image=fit:latest",
    ],
    plugins = [
        "itf.plugins.docker",
    ],
)
