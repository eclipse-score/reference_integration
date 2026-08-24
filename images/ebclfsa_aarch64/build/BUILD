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

genrule(
    name = "extract-fastdev-image",
    srcs = ["@eb_corbos_toolkit_fastdev_archive//file"],
    outs = [
        "ebcl-qemuarm64/fastdev-ubuntu-ebclfsa-ebcl-qemuarm64.wic",
        "ebcl-qemuarm64/fastdev-ubuntu-ebclfsa-ebcl-qemuarm64-vmlinux",
    ],
    cmd = "tar xzf $(location @eb_corbos_toolkit_fastdev_archive//file) -C $(RULEDIR)/ebcl-qemuarm64 && chmod +w $(RULEDIR)/ebcl-qemuarm64/fastdev-ubuntu-ebclfsa-ebcl-qemuarm64.wic && ls -lah $(RULEDIR)/ebcl-qemuarm64/fastdev-ubuntu-ebclfsa-ebcl-qemuarm64.wic > /tmp/foo",
    visibility = [
        "//visibility:public",
    ],
)

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
        ":extract-fastdev-image",
        ":crinit_config_tar",
        ":scripts_tar",
        "build_image.sh",
    ],
    outs = [
        "ebcl-qemuarm64-deployed/fastdev-ubuntu-ebclfsa-ebcl-qemuarm64.wic",
        "ebcl-qemuarm64-deployed/fastdev-ubuntu-ebclfsa-ebcl-qemuarm64-vmlinux",
    ],
    cmd = " \
        $(location build_image.sh) \
            $(RULEDIR) \
            $(RULEDIR)/ebcl-qemuarm64 \
            $(RULEDIR)/ebcl-qemuarm64-deployed \
            $(location //showcases:showcases_pkg_tar) \
            $(location :crinit_config_tar) \
            $(location :scripts_tar) \
    ",
    visibility = [
        "//visibility:public",
    ],
)
