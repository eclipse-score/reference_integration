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
"""TCK packaging rules.

Builds the score-tck-<version>.tar.gz bundle containing:
- bin/score-tck (self-contained runner)
- reference/sbom.spdx.json (golden SBOM)
- reference/requirements.json (requirement mappings)
- docs/USER_GUIDE.md
"""

load("@rules_pkg//pkg:pkg.bzl", "pkg_tar")

# Golden SBOM - copy from root product SBOM
alias(
    name = "golden_sbom",
    actual = "//:sbom",
    visibility = ["//visibility:public"],
)

# Requirements mapping - extracted from platform_integration_tests
genrule(
    name = "requirements_map",
    srcs = glob(["../platform_integration_tests/**/*.py"]),
    outs = ["requirements.json"],
    cmd = """
        python3 $(location :extract_requirements.py) $(SRCS) > $@
    """,
    tools = [":extract_requirements.py"],
)

py_binary(
    name = "extract_requirements.py",
    srcs = ["extract_requirements.py"],
    main = "extract_requirements.py",
)

# TCK package - assemble everything
pkg_tar(
    name = "score_tck_pkg",
    srcs = [
        ":golden_sbom",
        ":requirements_map",
        "//tck/bin:score-tck",
        "//tck/checks:sbom_check.py",
    ],
    package_dir = "score-tck-{version}",
    strip_prefix = ".",
    visibility = ["//visibility:public"],
)
