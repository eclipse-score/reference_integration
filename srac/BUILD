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
load("@rules_python//python:defs.bzl", "py_binary", "py_library")
load("@score_tooling//python_basics:defs.bzl", "score_py_pytest")

py_library(
    name = "profile",
    srcs = [
        "__init__.py",
        "tools/__init__.py",
        "tools/profile.py",
    ],
    visibility = ["//visibility:public"],
)

py_binary(
    name = "enrich_sbom",
    srcs = ["tools/enrich_sbom.py"],
    main = "tools/enrich_sbom.py",
    visibility = ["//visibility:public"],
    deps = [":profile"],
)

score_py_pytest(
    name = "tests",
    srcs = glob(["tests/**/*.py"]),
    data = [
        "examples/persistency-kvs.srac.json",
        "schema/srac.schema.json",
    ],
    pytest_config = "//:pyproject.toml",
    deps = [":profile"],
)

exports_files([
    "examples/persistency-kvs.srac.json",
    "schema/srac.schema.json",
])
