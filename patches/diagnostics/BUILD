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

load(":opensovd_build_stamp_test.bzl", "opensovd_build_stamp_test")

alias(
    name = "opensovd_stamp_env",
    actual = "@opensovd_build_stamp//:stamp.env",
    visibility = ["//visibility:public"],
)

alias(
    name = "opensovd_commit_date",
    actual = "@opensovd_build_stamp//:commit_date.txt",
    visibility = ["//visibility:public"],
)

opensovd_build_stamp_test(name = "opensovd_build_stamp_test")
