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
load("@rules_pkg//pkg:pkg.bzl", "pkg_deb")
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

pkg_deb(
    name = "platform_deb",
    architecture = "arm64",
    data = "//deploy:platform_tar",
    description = "S-CORE platform files for the fast-dev image",
    maintainer = "Eclipse S-CORE contributors",
    package = "score-reference-integration-platform",
    version = "1.0.0",
)

pkg_deb(
    name = "showcases_deb",
    architecture = "arm64",
    data = "//showcases:showcases_pkg_tar",
    description = "S-CORE showcases for the fast-dev image",
    maintainer = "Eclipse S-CORE contributors",
    package = "score-reference-integration-showcases",
    version = "1.0.0",
)

pkg_deb(
    name = "crinit_config_deb",
    architecture = "all",
    data = ":crinit_config_tar",
    description = "Crinit configuration for the fast-dev image",
    maintainer = "Eclipse S-CORE contributors",
    package = "score-reference-integration-crinit-config",
    replaces = ["ebclfsa-fastdev-crinit-getty"],
    version = "1.0.0",
)

pkg_deb(
    name = "scripts_deb",
    architecture = "all",
    data = ":scripts_tar",
    description = "Scripts for the fast-dev image",
    maintainer = "Eclipse S-CORE contributors",
    package = "score-reference-integration-scripts",
    version = "1.0.0",
)

genrule(
    name = "fastdev-image",
    # Keep the vanilla network configuration for QEMU user-mode networking;
    # the os_images network package is for the ITF bridge.
    srcs = [
        ":platform_deb",
        ":showcases_deb",
        "@os_images//ebclfsa_aarch64_prebuild:vanilla-image",
        "@os_images//ebclfsa_aarch64_prebuild:kernel",
        "@os_images//ebclfsa_aarch64:sshd_config_deb",
        ":crinit_config_deb",
        ":scripts_deb",
        "@os_images//ebclfsa_aarch64_prebuild:build_image.sh",
    ],
    outs = [
        "ebcl-qemuarm64-deployed/fastdev-trixie-ebclfsa-ebcl-qemuarm64.wic",
        "ebcl-qemuarm64-deployed/fastdev-trixie-ebclfsa-ebcl-qemuarm64-vmlinux",
    ],
    cmd = " \
        $(location @os_images//ebclfsa_aarch64_prebuild:build_image.sh) \
            $(RULEDIR) \
            $$(dirname $(location @os_images//ebclfsa_aarch64_prebuild:vanilla-image)) \
            $(RULEDIR)/ebcl-qemuarm64-deployed \
            $(location :platform_deb) \
            $(location :showcases_deb) \
            $(location @os_images//ebclfsa_aarch64:sshd_config_deb) \
            $(location :crinit_config_deb) \
            $(location :scripts_deb) \
    ",
    visibility = [
        "//visibility:public",
    ],
)
