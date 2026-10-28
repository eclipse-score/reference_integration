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

load("@rules_shell//shell:sh_binary.bzl", "sh_binary")
load("@rules_shell//shell:sh_test.bzl", "sh_test")

genrule(
    name = "image",
    srcs = [
        "kas.yml",
        "@eb_corbos_toolkit//:BUILD.bazel",
        "@eb_corbos_toolkit//:sources",
        "//showcases:showcases_deb",
        "//images/ebclfsa_aarch64/build/config-overlay:etc/crinit/crinit.d/getty-console.crinit",
        "//images/ebclfsa_aarch64/build/config-overlay:usr/bin/delayed-start.sh",
    ] + glob(["meta-score/**"]),
    outs = [
        "fastdev-trixie-ebclfsa-ebcl-qemuarm64-vmlinux",
        "fastdev-trixie-ebclfsa-ebcl-qemuarm64.wic",
    ],
    cmd = "bash $(location build_image.sh) " +
          "$$(dirname $(location @eb_corbos_toolkit//:BUILD.bazel)) " +
          "$(location //showcases:showcases_deb) " +
          "$(location kas.yml) " +
          "$(location //images/ebclfsa_aarch64/build/config-overlay:etc/crinit/crinit.d/getty-console.crinit) " +
          "$(location //images/ebclfsa_aarch64/build/config-overlay:usr/bin/delayed-start.sh) " +
          "$(RULEDIR)",
    local = True,
    tags = ["manual"],
    tools = ["build_image.sh"],
    visibility = ["//visibility:public"],
)

sh_binary(
    name = "run",
    srcs = ["//runners/qemu_aarch64/scripts:run_qemu.sh"],
    args = [
        "$(location :fastdev-trixie-ebclfsa-ebcl-qemuarm64-vmlinux)",
        "$(location :fastdev-trixie-ebclfsa-ebcl-qemuarm64.wic)",
        "-append",
        "'root=/dev/vda1 sdk_enable lisa_syscall_whitelist=2026 rw sharedmem.enable_sharedmem=0 init=/usr/bin/ebclfsa-cflinit'",
        "-snapshot",
    ],
    data = [
        ":fastdev-trixie-ebclfsa-ebcl-qemuarm64.wic",
        ":fastdev-trixie-ebclfsa-ebcl-qemuarm64-vmlinux",
    ],
    tags = ["manual"],
    use_bash_launcher = True,
    visibility = ["//visibility:public"],
)

sh_test(
    name = "build_image_test",
    size = "small",
    srcs = ["build_image_test.sh"],
    data = [
        "build_image.sh",
        "kas.yml",
        "//images/ebclfsa_aarch64/build/config-overlay:etc/crinit/crinit.d/getty-console.crinit",
        "//images/ebclfsa_aarch64/build/config-overlay:usr/bin/delayed-start.sh",
    ] + glob(["meta-score/**"]),
)
