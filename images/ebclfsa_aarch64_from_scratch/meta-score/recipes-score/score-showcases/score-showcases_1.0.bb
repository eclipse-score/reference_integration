# Copyright (c) 2026 Contributors to the Eclipse Foundation
# SPDX-License-Identifier: Apache-2.0

SUMMARY = "Bazel-built Eclipse S-CORE showcases"
LICENSE = "Apache-2.0"

inherit dpkg-prebuilt

SRC_URI = "file://score-showcases_1.0_arm64.deb"
COMPATIBLE_MACHINE = "ebcl-qemuarm64"
