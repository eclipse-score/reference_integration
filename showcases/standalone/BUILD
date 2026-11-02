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
load("@score_lifecycle//:defs.bzl", "launch_manager_config")
load("//bazel_common:bundlers.bzl", "score_pkg_bundle")

score_pkg_bundle(
    name = "comm",
    bins = ["@score_communication//score/mw/com/example/com-api-example:com-api-example"],
    config_data = [
        "//showcases/standalone:com.score.json",
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

score_pkg_bundle(
    name = "config_management",
    bins = [
        "@score_config_management//score/config_management/config_daemon/code:config_daemon",
    ],
    config_data = [
        "//showcases/standalone:config_management.score.json",
    ],
    custom_layout = {
        "@score_config_management//score/config_management/config_daemon/code/services/details/mw_com:mw_com_config": "etc/mw_com_config.json",
        "@score_config_management//score/config_management/config_daemon/code/plugins/demo_json:demo_parameters": "etc/demo_parameters.json",
    },
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

launch_manager_config(
    name = "lifecycle_extras_configs",
    config = "//showcases/standalone/configs:lifecycle_extras_lm_config.json",
    flatbuffer_out_dir = "etc",
)

# launch_manager, control_daemon, cpp/rust_supervised_app and lifecycle_signal.sh
# are shipped by //showcases/simple_lifecycle into the shared /showcases/bin.
score_pkg_bundle(
    name = "lifecycle_extras",
    bins = [
        "@score_lifecycle//examples/c_supervised_app",
        "@score_lifecycle//examples/cpp_lifecycle_app",
        "@score_lifecycle//examples/control_application:lmcontrol",
    ],
    config_data = ["//showcases/standalone:lifecycle_extras.score.json"],
    custom_layout = {
        ":lifecycle_extras_configs": "etc/",
        "//showcases/simple_lifecycle/configs:logging.json": "etc/logging.json",
    },
    package_dir = "standalone",
)
