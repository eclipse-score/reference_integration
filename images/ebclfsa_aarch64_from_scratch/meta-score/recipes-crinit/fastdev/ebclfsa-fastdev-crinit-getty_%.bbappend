# Copyright (c) 2026 Contributors to the Eclipse Foundation
# SPDX-License-Identifier: Apache-2.0

FILESEXTRAPATHS:prepend := "${THISDIR}/files:"
SRC_URI += "file://delayed-start.sh"

do_install:append() {
    install -d ${D}/usr/bin
    install -m 0755 ${WORKDIR}/delayed-start.sh ${D}/usr/bin/delayed-start.sh
}
