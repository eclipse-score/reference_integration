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

load("@rules_python//sphinxdocs:sphinx.bzl", "sphinx_build_binary", "sphinx_docs")
load("@score_docs_as_code//:docs.bzl", "docs")

docs(
    data = [
        # "@score_platform//:",
        "@score_process//:sphinx_docs_library",
        "@score_baselibs//:sphinx_docs_library",
        # Persistency cannot be included, as it does not contain any needs.
        # -> sphinx-needs bug?
        # "@score_persistency//:needs_json",
    ],
    source_dir = "docs",
    deps = [
    ],
)

source_dir = "docs"

sphinx_docs(
    name = "html",
    srcs = glob(
        [
            source_dir + "/**/*.png",
            source_dir + "/**/*.svg",
            source_dir + "/**/*.md",
            source_dir + "/**/*.rst",
            source_dir + "/**/*.html",
            source_dir + "/**/*.css",
            source_dir + "/**/*.puml",
            source_dir + "/**/*.need",
            source_dir + "/**/*.yaml",
            source_dir + "/**/*.json",
            source_dir + "/**/*.csv",
            source_dir + "/**/*.inc",
            "more_docs/**/*.rst",
        ],
        allow_empty = True,
    ),
    config = ":" + source_dir + "/conf.py",
    extra_opts = [
        "-W",
        "--keep-going",
        "-T",  # show more details in case of errors
        "--jobs",
        "auto",
    ],
    formats = ["html"],
    sphinx = ":sphinx_build",
    tools = [],
    visibility = ["//visibility:public"],
    # Modules export their docs as sphinx_docs_library
    # which are imported by bazel to docs/modules/<module_name>
    deps = [
        "@score_platform//:sphinx_docs_library",
        "@score_process//:sphinx_docs_library",
        "@score_baselibs//:sphinx_docs_library",
        # "@score_persistency//:sphinx_docs_library",
        # "@score_communication//:sphinx_docs_library"
    ],
)

# Simple filegroup target to demonstrate the build system works
filegroup(
    name = "readme",
    srcs = ["README.md"],
    visibility = ["//visibility:public"],
)
