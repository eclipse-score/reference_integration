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

load("@rules_pkg//pkg:tar.bzl", "pkg_tar")

genrule(
    name = "extract-fastdev-image",
    srcs = ["@eb_corbos_toolkit_fastdev_rpi4b_archive//file"],
    outs = ["ebcl-rpi4b/fastdev-trixie-ebclfsa-rpi4b.wic"],
    cmd = "mkdir -p $(RULEDIR)/ebcl-rpi4b && tar xzf $(location @eb_corbos_toolkit_fastdev_rpi4b_archive//file) -C $(RULEDIR)/ebcl-rpi4b && chmod +w $(RULEDIR)/ebcl-rpi4b/fastdev-trixie-ebclfsa-rpi4b.wic",
)

# Only the init task of the diagnostics: the console of the Raspberry Pi image is the serial one.
pkg_tar(
    name = "crinit_config_tar",
    srcs = [
        "//images/ebclfsa_aarch64/build/config-overlay:etc/crinit/crinit.d/diagnostics.crinit",
    ],
    mode = "0755",
    package_dir = "/etc/crinit/crinit.d",
)

# The static address of the image, replacing /etc/config/network of the base image. Set at build time
# with SCORE_PI_ADDRESS, SCORE_PI_GATEWAY and SCORE_PI_DNS, see images/network/README.md.
pkg_tar(
    name = "network_config_tar",
    srcs = ["@score_pi_network//:netifd/network"],
    mode = "0644",
    package_dir = "/etc/config",
)

genrule(
    name = "fastdev-image",
    srcs = [
        "//deploy:platform_tar",
        "//showcases:showcases_pkg_tar",
        ":extract-fastdev-image",
        ":crinit_config_tar",
        ":network_config_tar",
        "//images/network:diagnostics_config_tar",
        "build_image.py",
    ],
    outs = ["ebcl-rpi4b-deployed/fastdev-trixie-ebclfsa-rpi4b.wic"],
    cmd = " ".join([
        "python3 $(location build_image.py)",
        "$(location :extract-fastdev-image)",
        "$@",
        "$(location //deploy:platform_tar)",
        "$(location //showcases:showcases_pkg_tar)",
        "$(location :crinit_config_tar)",
        "$(location :network_config_tar)",
        "$(location //images/network:diagnostics_config_tar)",
    ]),
    visibility = [
        "//visibility:public",
    ],
)

exports_files(
    ["build_image.py"],
    visibility = ["//images/rpios_rpi4b:__pkg__"],
)
