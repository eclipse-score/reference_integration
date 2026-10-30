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
load("@rules_cc//cc:cc_binary.bzl", "cc_binary")
load("@rules_rust//rust:defs.bzl", "rust_binary")
load("//bazel_common:bundlers.bzl", "score_pkg_bundle")

_COM_API_DEPS = [
    "@score_communication//score/mw/com/example/com-api-example/com-api-gen",
    "@score_communication//score/mw/com/rust:score_com",
]

_CC_COM_API_DEPS = [
    "@score_communication//score/mw/com",
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

cc_binary(
    name = "fit_sender_cc",
    srcs = [
        "fit_sender.cc",
        "vehicle_interface.h",
    ],
    visibility = ["//visibility:public"],
    deps = _CC_COM_API_DEPS,
)

cc_binary(
    name = "fit_receiver_cc",
    srcs = [
        "fit_receiver.cc",
        "vehicle_interface.h",
    ],
    visibility = ["//visibility:public"],
    deps = _CC_COM_API_DEPS,
)

score_pkg_bundle(
    name = "comm_fit",
    bins = [
        ":fit_sender",
        ":fit_receiver",
        ":fit_sender_cc",
        ":fit_receiver_cc",
    ],
)
