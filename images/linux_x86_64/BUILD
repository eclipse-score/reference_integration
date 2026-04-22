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
load("@rules_oci//oci:defs.bzl", "oci_image", "oci_load")
load("@rules_pkg//pkg:tar.bzl", "pkg_tar")
load("@rules_shell//shell:sh_binary.bzl", "sh_binary")

sh_binary(
    name = "run",
    srcs = [
        "//runners/docker_x86_64/scripts:run_docker",
    ],
    args = [
        "$(location :image_load)",
    ],
    data = [
        ":image_load",
    ],
    env = {
        "OCI_IMAGE": "score_showcases:latest",
    },
)

pkg_tar(
    name = "datarouter_bin_tar",
    srcs = ["@score_logging//score/datarouter"],
    mode = "0755",
    package_dir = "/usr/bin/datarouter",
)

pkg_tar(
    name = "opensovd_cda_bin_tar",
    srcs = ["@score_opensovd_cda//:opensovd-cda"],
    mode = "0755",
    package_dir = "/usr/bin/opensovd_cda_bin",
)

pkg_tar(
    name = "datarouter_etc_tar",
    srcs = [
        "//feature_integration_tests/configs/datarouter:etc/log-channels.json",
        "//feature_integration_tests/configs/datarouter:etc/logging.json",
    ],
    mode = "0644",
    package_dir = "/usr/bin/datarouter/etc",
)

oci_image(
    name = "image",
    base = "@ubuntu_22_04_linux_amd64",
    tars = [
        "//showcases:showcases_pkg_tar",
        ":datarouter_bin_tar",
        ":datarouter_etc_tar",
        ":opensovd_cda_bin_tar",
    ],
)

oci_load(
    name = "image_load",
    image = ":image",
    repo_tags = ["score_showcases:latest"],
    visibility = [
        "//feature_integration_tests/itf:__pkg__",
    ],
)
