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
load("@rules_shell//shell:sh_binary.bzl", "sh_binary")
load("@rules_oci//oci:defs.bzl", "oci_image", "oci_tarball")
load("@rules_pkg//pkg:tar.bzl", "pkg_tar")

alias(
    name = "image",
    actual = "//showcases:showcases_all",
    visibility = ["//visibility:public"],
)

sh_binary(
    name = "run",
    srcs = ["//runners/docker_x86_64/scripts:run_docker.sh"],
    args = [
        "$(location :image)",
    ],
    data = [
        ":image",
    ],
)

pkg_tar(
    name = "showcases_archive",
    srcs = [
        "//showcases:showcases_all",
    ],
    symlinks = {
        "showcases": "showcases_all",
    }
)

oci_image(
    name = "docker_image",
    base = "@ubuntu_22_04",
    tars = [
        ":showcases_archive",
    ],
)

oci_tarball(
    name = "docker_image_tarball",
    image = ":docker_image",
    repo_tags = ["score_showcases:latest"],
    visibility = [
        "//feature_integration_tests/itf:__pkg__",
    ],
)

