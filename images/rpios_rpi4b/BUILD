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

# Raspberry Pi OS Lite (64-bit, Trixie) for the Raspberry Pi 4B with the S-CORE platform, the
# showcases and the diagnostics deployed in it, for integration testing. The release image of
# Raspberry Pi OS is downloaded and checked by its sha256 (bazel_common/score_images.MODULE.bazel).
# It allows root login without a password, like the QEMU image, so it is not for production.
#
# Build with the Linux aarch64 configuration, the one of the release archives:
#   bazel build --config=linux-aarch64 //images/rpios_rpi4b:image
# The result is bazel-bin/images/rpios_rpi4b/deployed/raspios-rpi4b.wic, to flash to an SD card.

# The image is grown to 4 GiB: the release image has only a few hundred MiB free.
genrule(
    name = "prepared",
    srcs = [
        "@raspios_lite_arm64//file",
        "build/prepare.py",
    ],
    outs = ["prepared/raspios-rpi4b.wic"],
    cmd = "xz -dc $(location @raspios_lite_arm64//file) > $(@) && python3 $(location build/prepare.py) $(@) --size 4294967296",
)

# The unit that starts the diagnostics stack at boot, enabled in multi-user.target.
pkg_tar(
    name = "systemd_config_tar",
    srcs = ["build/diagnostics.service"],
    mode = "0644",
    package_dir = "/etc/systemd/system",
    symlinks = {
        "/etc/systemd/system/multi-user.target.wants/diagnostics.service": "/etc/systemd/system/diagnostics.service",
    },
)

genrule(
    name = "image",
    srcs = [
        ":prepared",
        ":systemd_config_tar",
        "//deploy:platform_tar",
        "//showcases:showcases_pkg_tar",
        "//images/ebclfsa_rpi4b/build:build_image.py",
    ],
    outs = ["deployed/raspios-rpi4b.wic"],
    cmd = " ".join([
        "python3 $(location //images/ebclfsa_rpi4b/build:build_image.py)",
        "$(location :prepared)",
        "$@",
        "$(location //deploy:platform_tar)",
        "$(location //showcases:showcases_pkg_tar)",
        "$(location :systemd_config_tar)",
    ]),
    visibility = ["//visibility:public"],
)
