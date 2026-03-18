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

genrule(
    name = "fastdev-image",
    srcs = [
        "//showcases",
        "//feature_integration_tests/configs:etc_configs",
        ":extract-fastdev-image",
        ":config-overlay",
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
            $(location //showcases:showcases)/* \
            $(location :config-overlay)/* \
    ",
    visibility = [
        "//visibility:public",
    ],
)
