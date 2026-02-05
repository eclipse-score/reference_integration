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

load("@score_toolchains_qnx//rules/fs:ifs.bzl", "qnx_ifs")

filegroup(
    name = "scripts",
    srcs = [
        "//configs:startup.sh",
    ],
    visibility = ["//visibility:private"],
)

filegroup(
    name = "configs",
    srcs = [
        "//configs:pci_server.cfg",
        "//configs:pci_hw.cfg",
        "//configs:qcrypto.conf",
        "//configs:passwd",
        "//configs:group",
        "//configs:sshd_config",
        "//configs:ssh_host_rsa_key",
        "//configs:ssh_host_rsa_key.pub",
        "//configs:hostname",
        "//configs:network_setup.sh",
        "//configs:network_capture.sh",
        "//configs:profile",
        "//configs:dhcpcd.conf",
        "//configs:network_setup_dhcp.sh",
    ],
    visibility = ["//visibility:private"],
)

filegroup(
    name = "lifecycle_launch_manager",
    srcs = [
        "@score_lifecycle_health//src/launch_manager_daemon:launch_manager",
    ],
    visibility = ["//visibility:public"],
)

qnx_ifs(
    name = "init",
    build_file = "init.build",
    srcs = [
        "system.build",
        ":scripts",
        ":configs",
        "@score_scrample//src:scrample",
        "//scrample_integration:etc_configs",
        "@score_persistency//tests/cpp_test_scenarios:cpp_test_scenarios",
        "@score_lifecycle_health//src/launch_manager_daemon:launch_manager",
        "@score_lifecycle_health//examples/cpp_supervised_app",
        "@score_lifecycle_health//examples/control_application:control_daemon",
        "//lifecycle_integration:generate_launch_manager_config",
        "//lifecycle_integration:generate_launch_manager_health_config",
        "//lifecycle_integration:generate_supervised_app_health_config",
        "@score_lifecycle_health//examples/control_application:lmcontrol",
        "//lifecycle_integration:lifecycle_start"
    ],
    ext_repo_maping = {
        "SCRAMPLE_PATH": "$(location @score_scrample//src:scrample)",
        "CPP_TEST_SCENARIOS_PATH": "$(location @score_persistency//tests/cpp_test_scenarios:cpp_test_scenarios)",
        "LIFECYCLE_LAUNCH_MANAGER_EXE": "$(location @score_lifecycle_health//src/launch_manager_daemon:launch_manager)",
        "LIFECYCLE_LAUNCH_MANAGER_LM_CONFIG": "$(location //lifecycle_integration:generate_launch_manager_config)",
        "LIFECYCLE_LAUNCH_MANAGER_HM_CONFIG": "$(location //lifecycle_integration:generate_launch_manager_health_config)",
        "LIFECYCLE_CPP_SUPERVISED_APP_EXE": "$(location @score_lifecycle_health//examples/cpp_supervised_app)",
        "LIFECYCLE_CPP_SUPERVISED_APP_CONFIG": "$(location //lifecycle_integration:generate_supervised_app_health_config)",
        "LIFECYCLE_STATE_MANAGER_EXE": "$(location @score_lifecycle_health//examples/control_application:control_daemon)",
        "LIFECYCLE_STATE_MANAGER_CONTROL" : "$(location @score_lifecycle_health//examples/control_application:lmcontrol)",
        "LIFECYCLE_DEMO_START": "$(location //lifecycle_integration:lifecycle_start)"
    },
    visibility = [
        "//:__pkg__"
    ],
)
