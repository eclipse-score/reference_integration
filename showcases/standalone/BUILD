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
load("@rules_cc//cc:defs.bzl", "cc_binary")
load("//bazel_common:bundlers.bzl", "score_pkg_bundle")

# Consumer of the heartbeat service deployed by //deploy/communication. It
# brings no provider of its own, so it fails if the platform does not deploy one.
cc_binary(
    name = "heartbeat_consumer",
    srcs = ["heartbeat_consumer.cpp"],
    deps = [
        "//deploy/communication:heartbeat_interface",
        "@score_baselibs//score/string_manipulation/arguments",
        "@score_communication//score/mw/com",
    ],
)

score_pkg_bundle(
    name = "comm",
    bins = [
        "@score_communication//score/mw/com/example/com-api-example:com-api-example",
        "//showcases/standalone:heartbeat_consumer",
    ],
    config_data = [
        "//showcases/standalone:com.score.json",
        "//showcases/standalone:com_heartbeat.score.json",
    ],
    custom_layout = {
        "@score_communication//score/mw/com/example/com-api-example:etc/mw_com_config.json": "etc/mw_com_config.json",
    },
    package_dir = "standalone",
)

score_pkg_bundle(
    name = "kyron",
    bins = [
        "@score_kyron//examples:select",
        "@score_kyron//examples:safety_task",
        "@score_kyron//examples:main_macro",
    ],
    config_data = [
        "//showcases/standalone:kyron.score.json",
    ],
    package_dir = "standalone",
)

score_pkg_bundle(
    name = "time",
    bins = [
        "@score_time//examples/time/vehicle_time",
        "@score_time//examples/time/system_time",
        "@score_time//examples/time/steady_time",
        "@score_time//examples/time/high_res_steady_time",
    ],
    config_data = [
        "//showcases/standalone:time.score.json",
    ],
    package_dir = "standalone",
)

score_pkg_bundle(
    name = "logging",
    bins = [
        "@score_logging//score/test/component/logging_app:logging_app",
        "@score_logging//score/test/component/dlt_generator_app:dlt_generator",
    ],
    config_data = [
        "//showcases/standalone:logging.score.json",
    ],
    custom_layout = {
        "//showcases/standalone/configs:logging_app.json": "logging_app/etc/logging.json",
        "//showcases/standalone/configs:dlt_generator.json": "dlt_generator/etc/logging.json",
    },
    package_dir = "standalone",
)

# The config daemon and its configuration are part of the deployed platform
# (//deploy/config_management). This showcase only contributes the manifest
# that drives the deployed daemon.
score_pkg_bundle(
    name = "config_management",
    bins = [],
    config_data = [
        "//showcases/standalone:config_management.score.json",
    ],
    package_dir = "standalone",
)

# Persistency has no runnable showcase yet; the upstream test scenarios binary
# is shipped so that one can be added without changing the image layout.
# score_pkg_bundle names binaries after their label, hence the alias.
alias(
    name = "cpp_tests_persistency",
    actual = "@score_persistency//score/kvs/tests/test_scenarios/cpp:test_scenarios",
)

score_pkg_bundle(
    name = "persistency",
    bins = ["//showcases/standalone:cpp_tests_persistency"],
    package_dir = "standalone",
)

score_pkg_bundle(
    name = "baselibs",
    bins = [
        "@score_baselibs//examples/log_builtin:log_builtin",
        "@score_baselibs//examples/log_custom:log_custom",
        "@score_baselibs//examples/log_cpp_init:log_cpp_init",
    ],
    config_data = ["//showcases/standalone:baselibs.score.json"],
    package_dir = "standalone",
)
