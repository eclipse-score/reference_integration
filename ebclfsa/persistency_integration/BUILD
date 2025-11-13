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
load("@score_baselibs//score/language/safecpp:toolchain_features.bzl", "COMPILER_WARNING_FEATURES")

genrule(
    name = "fetch-fastdev-archive",
    srcs = [],
    outs = ["fastdev-archive.tgz"],
    cmd = "wget -O $@ https://github.com/Elektrobit/eclipse-score_toolchains_gcc/releases/download/0.5.0-alpha/fastdev-ubuntu-ebcl-deb-qemu-arm64.tgz"
)

genrule(
    name = "fastdev-image",
    srcs = [":fetch-fastdev-archive"],
    outs = [
        "deb-qemuarm64/fastdev-ubuntu-ebcl-deb-qemuarm64.wic",
        "deb-qemuarm64/fastdev-ubuntu-ebcl-deb-qemuarm64-vmlinux"
    ],
    cmd = "tar xzf $(location :fetch-fastdev-archive) -C $(RULEDIR)",
)

genrule(
    name = "upload",
    srcs = [
        "@score_persistency//tests/cpp_test_scenarios:cpp_test_scenarios",
        ":fastdev-image",
        "scripts/cpp_tests_persistency.sh",
        "run_qemu.sh",
    ],
    cmd = " \
        mkdir -p $(RULEDIR)/deb-qemuarm64-modified &&\
        cp $(RULEDIR)/deb-qemuarm64/* $(RULEDIR)/deb-qemuarm64-modified/ &&\
        $(location run_qemu.sh) $(RULEDIR)/deb-qemuarm64-modified -pidfile $(RULEDIR)/qemu.pid > $(RULEDIR)/qemu_upload.log &\
        sleep 30 ; \
        sshpass -p linux scp -o StrictHostKeyChecking=no -P 2222 $(location @score_persistency//tests/cpp_test_scenarios:cpp_test_scenarios) root@localhost:/usr/bin/cpp_tests_persistency &&\
        sshpass -p linux scp -o StrictHostKeyChecking=no -P 2222 $(location scripts/cpp_tests_persistency.sh) root@localhost:/usr/bin/cpp_tests_persistency.sh &&\
        sshpass -p linux ssh -o StrictHostKeyChecking=no -p 2222 root@localhost sync &&\
        sshpass -p linux ssh -o StrictHostKeyChecking=no -p 2222 root@localhost crinit-ctl poweroff || true \
        sleep 5  \
    ",
    outs = [
        "qemu_upload.log",
        "deb-qemuarm64-modified/fastdev-ubuntu-ebcl-deb-qemuarm64.wic",
        "deb-qemuarm64-modified/fastdev-ubuntu-ebcl-deb-qemuarm64-vmlinux"
    ],
)

genrule(
    name = "run",
    srcs = [
        "deb-qemuarm64-modified/fastdev-ubuntu-ebcl-deb-qemuarm64.wic",
        "deb-qemuarm64-modified/fastdev-ubuntu-ebcl-deb-qemuarm64-vmlinux",
        "run_qemu.sh"
    ],
    cmd = " \
        $(location run_qemu.sh) $(RULEDIR)/deb-qemuarm64-modified -pidfile $(RULEDIR)/qemu.pid > $(RULEDIR)/qemu_run.log &\
        sleep 10 ; \
        sshpass -p linux ssh -o StrictHostKeyChecking=no -p 2222 root@localhost cpp_tests_persistency.sh > $(RULEDIR)/ssh_persistency_test_scenarios_run.log && \
        sshpass -p linux ssh -o StrictHostKeyChecking=no -p 2222 root@localhost crinit-ctl poweroff || true \
        sleep 5 \
    ",
    outs = [
        "qemu_run.log",
        "ssh_persistency_test_scenarios_run.log",
    ],
)
