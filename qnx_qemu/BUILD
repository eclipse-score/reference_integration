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



sh_binary(
    name = "run_qemu",
    srcs = ["scripts/run_qemu.sh"],
    args = [
        "$(location @toolchains_qnx_sdp//:host_dir)",
        "$(location //build:init)",
    ],
    data = [
        "//build:init",
        "@toolchains_qnx_sdp//:host_all",
        "@toolchains_qnx_sdp//:host_dir",
    ],
)

sh_binary(
    name = "test_qemu",
    srcs = ["test/test_qnx_qemu.sh"],
    args = [
        "$(location @toolchains_qnx_sdp//:host_dir)",
        "$(location //build:init)",
        "--timeout=90",
        "--ssh-port=2222", 
        "--boot-wait=15",
    ],
    data = [
        "//build:init",
        "@toolchains_qnx_sdp//:host_all",
        "@toolchains_qnx_sdp//:host_dir",
    ],
)
