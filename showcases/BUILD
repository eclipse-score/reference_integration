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
load("//bazel_common:bundlers.bzl", "score_pkg_bundle")

score_pkg_bundle(
    name = "showcases_all",
    bins = ["//showcases/cli" ],
    other_package_files = [
        "//showcases/standalone:comm_pkg_files",
        "//showcases/standalone:kyron_pkg_files",
        "//showcases/orchestration_persistency:orch_per_pkg_files",
        "//showcases/simple_lifecycle:simple_lifecycle_pkg_files",
    ],
 
)


