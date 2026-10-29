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

sh_test(
    name = "linux_aarch64_elf_compatibility_test",
    srcs = ["linux_aarch64_elf_compatibility_test.sh"],
    args = ["$(location //showcases:showcases_pkg_tar)"],
    data = ["//showcases:showcases_pkg_tar"],
    tags = [
        "linux-aarch64",
        "requires-linux-aarch64-toolchain",
    ],
    # Only run on Linux AArch64 platforms
    target_compatible_with = [
        "@platforms//os:linux",
        "@platforms//cpu:aarch64",
    ],
)
