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
load("@rules_python//python:defs.bzl", "py_library")
load("@score_tooling//python_basics:defs.bzl", "score_py_pytest")

py_library(
    name = "prepare_lib",
    srcs = ["build/prepare.py"],
    imports = ["build"],
)

score_py_pytest(
    name = "prepare_test",
    srcs = ["prepare_test.py"],
    pytest_config = "//:pyproject.toml",
    deps = [":prepare_lib"],
)

config_setting(
    name = "linux_aarch64",
    constraint_values = [
        "@platforms//cpu:aarch64",
        "@platforms//os:linux",
        "@score_bazel_platforms//runtime_es:posix",
        "@score_bazel_platforms//version:gcc_12.2.0",
    ],
)

# Raspberry Pi OS Lite (64-bit, Trixie) for the Raspberry Pi 4B with the S-CORE platform, the
# showcases and the diagnostics deployed in it, for integration testing. The release image of
# Raspberry Pi OS is downloaded and checked by its sha256 (bazel_common/score_images.MODULE.bazel).
# Empty passwords are locked; provision unique credentials before using SSH. Not for production.
#
# The address is static, 192.168.7.2/24 unless SCORE_PI_ADDRESS, SCORE_PI_GATEWAY and SCORE_PI_DNS are set
# (images/network/README.md).
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

# The static address of the image, as the NetworkManager profile of eth0 (it takes the place of the
# automatic DHCP connection). NetworkManager ignores profiles that others can read, hence mode 0600. Set
# at build time with SCORE_PI_ADDRESS, SCORE_PI_GATEWAY and SCORE_PI_DNS, see images/network/README.md.
pkg_tar(
    name = "network_config_tar",
    srcs = ["@score_pi_network//:networkmanager/score-static.nmconnection"],
    mode = "0600",
    package_dir = "/etc/NetworkManager/system-connections",
)

genrule(
    name = "image",
    srcs = [
        ":prepared",
        ":systemd_config_tar",
        ":network_config_tar",
        "//images/network:diagnostics_config_tar",
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
        "$(location :network_config_tar)",
        "$(location //images/network:diagnostics_config_tar)",
    ]),
    target_compatible_with = select({
        ":linux_aarch64": [],
        "//conditions:default": ["@platforms//:incompatible"],
    }),
    visibility = ["//visibility:public"],
)
