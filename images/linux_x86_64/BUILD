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
load("@rules_oci//oci:defs.bzl", "oci_image", "oci_tarball")
load("@rules_pkg//pkg:tar.bzl", "pkg_tar")
load("@rules_shell//shell:sh_binary.bzl", "sh_binary")

sh_binary(
    name = "run",
    srcs = ["//runners/docker_x86_64/scripts:run_docker.sh"],
    args = [
        "$(location :image_tarball)",
    ],
    data = [
        ":image_tarball",
    ],
    env = {
        "OCI_IMAGE": "score_showcases:latest",
    },
)

oci_image(
    name = "image",
    base = "@ubuntu_22_04",
    tars = [
        "//showcases:showcases_pkg_tar",
    ],
)

oci_tarball(
    name = "image_tarball",
    image = ":image",
    repo_tags = ["score_showcases:latest"],
    visibility = [
        "//feature_integration_tests/itf:__pkg__",
    ],
)
