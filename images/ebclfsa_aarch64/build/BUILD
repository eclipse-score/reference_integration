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
load("@rules_pkg//pkg:tar.bzl", "pkg_tar")

pkg_tar(
    name = "crinit_config_tar",
    srcs = [
        "//images/ebclfsa_aarch64/build/config-overlay:etc/crinit/crinit.d/getty-console.crinit",
    ],
    mode = "0755",
    package_dir = "/etc/crinit/crinit.d",
)

pkg_tar(
    name = "scripts_tar",
    srcs = [
        "//images/ebclfsa_aarch64/build/config-overlay:usr/bin/delayed-start.sh",
    ],
    mode = "0755",
    package_dir = "/usr/bin",
)

genrule(
    name = "fastdev-image",
    srcs = [
        "//showcases:showcases_pkg_tar",
        "//feature_integration_tests/configs:etc_configs",
        "@os_images//ebclfsa_aarch64:vanilla-image",
        "@os_images//ebclfsa_aarch64:kernel",
        ":crinit_config_tar",
        ":scripts_tar",
        "@os_images//scripts:build_ebclfsa_aarch64_image.sh",
    ],
    outs = [
        "ebcl-qemuarm64-deployed/fastdev-trixie-ebclfsa-ebcl-qemuarm64.wic",
        "ebcl-qemuarm64-deployed/fastdev-trixie-ebclfsa-ebcl-qemuarm64-vmlinux",
    ],
    cmd = " \
        $(location @os_images//scripts:build_ebclfsa_aarch64_image.sh) \
            $(RULEDIR) \
            $$(dirname $(location @os_images//ebclfsa_aarch64:vanilla-image)) \
            $(RULEDIR)/ebcl-qemuarm64-deployed \
            $(location //showcases:showcases_pkg_tar) \
            $(location :crinit_config_tar) \
            $(location :scripts_tar) \
    ",
    visibility = [
        "//visibility:public",
    ],
)
