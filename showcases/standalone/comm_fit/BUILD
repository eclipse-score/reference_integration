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
load("@rules_rust//rust:defs.bzl", "rust_binary")
load("//bazel_common:bundlers.bzl", "score_pkg_bundle")

# Separate producer/receiver binaries for the communication ITF. Upstream
# replaced the two-process ipc_bridge example with the single-process
# com-api-example, so these provide the distinct sender/receiver processes the
# ITF needs to observe delivery, ordering and value-integrity over real shared
# memory. They reuse com-api-example's VehicleInterface (exposed via
# //patches/communication:002-expose-com-api-gen.patch) and its deployed
# mw_com_config.json, so no separate deployment config is required.

_COM_API_DEPS = [
    "@score_communication//score/mw/com/example/com-api-example/com-api-gen",
    "@score_communication//score/mw/com/impl/rust/com-api/com-api",
]

rust_binary(
    name = "fit_sender",
    srcs = ["fit_sender.rs"],
    features = ["link_std_cpp_lib"],
    visibility = ["//visibility:public"],
    deps = _COM_API_DEPS,
)

rust_binary(
    name = "fit_receiver",
    srcs = ["fit_receiver.rs"],
    features = ["link_std_cpp_lib"],
    visibility = ["//visibility:public"],
    deps = _COM_API_DEPS,
)

score_pkg_bundle(
    name = "comm_fit",
    bins = [
        ":fit_sender",
        ":fit_receiver",
    ],
)
