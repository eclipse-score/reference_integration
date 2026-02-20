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

filegroup(
    name = "scripts",
    srcs = [
        "//integration/images/ebclfsa_aarch64/persistency_integration/scripts:startup.sh",
    ],
    visibility = ["//visibility:private"],
)

filegroup(
    name = "configs",
    srcs = [
        "//integration/images/ebclfsa_aarch64/scrample_integration/etc:logging.json",
        "//integration/images/ebclfsa_aarch64/scrample_integration/etc:mw_com_config.json",
    ],
    visibility = ["//visibility:private"],
)

genrule(
    name = "fetch-fastdev-archive",
    srcs = [],
    outs = ["fastdev-archive.tgz"],
    cmd = "wget -O $@ https://github.com/elektrobit-contrib/eclipse-score_toolchains_gcc/releases/download/0.5.0-beta/fastdev-ubuntu-ebcl-deb-qemu-arm64.tgz"
)

genrule(
    name = "extract-fastdev-image",
    srcs = [":fetch-fastdev-archive"],
    outs = [
        "ebcl-qemuarm64/fastdev-ubuntu-ebclfsa-ebcl-qemuarm64.wic",
        "ebcl-qemuarm64/fastdev-ubuntu-ebclfsa-ebcl-qemuarm64-vmlinux"
    ],
    cmd = "tar xzf $(location :fetch-fastdev-archive) -C $(RULEDIR) && chmod +w $(RULEDIR)/ebcl-qemuarm64/fastdev-ubuntu-ebclfsa-ebcl-qemuarm64.wic && ls -lah $(RULEDIR)/ebcl-qemuarm64/fastdev-ubuntu-ebclfsa-ebcl-qemuarm64.wic > /tmp/foo",
    visibility = [
        "//visibility:public",
    ],
)

genrule(
    name = "fastdev-image",
    srcs = [
        #"@score_scrample//src:scrample",
        "//showcases:showcases_all",
        "@score_persistency//tests/test_scenarios/cpp:test_scenarios",
        "//feature_integration_tests/configs:etc_configs",
        ":extract-fastdev-image",
        "cpp_tests_persistency.sh",
        "etc/mw_com_config.json",
        "etc/logging.json",
        "run_qemu.sh",
    ],
    cmd = " \
        mkdir -p $(RULEDIR)/ebcl-qemuarm64-deployed &&\
        cp $(RULEDIR)/ebcl-qemuarm64/* $(RULEDIR)/ebcl-qemuarm64-deployed/ &&\
        $(location run_qemu.sh) $(RULEDIR)/ebcl-qemuarm64-deployed -pidfile $(RULEDIR)/qemu.pid > $(RULEDIR)/qemu_deployment.log &\
        sleep 30 ; \
        sshpass -p linux scp -o StrictHostKeyChecking=no -P 2222 $(location cpp_tests_persistency.sh) root@localhost:/usr/bin/ &&\
        sshpass -p linux scp -o StrictHostKeyChecking=no -P 2222 $(location etc/mw_com_config.json) root@localhost:/etc/ &&\
        sshpass -p linux scp -o StrictHostKeyChecking=no -P 2222 $(location etc/logging.json) root@localhost:/etc/ &&\
        sshpass -p linux ssh -o StrictHostKeyChecking=no -p 2222 root@localhost sync &&\
        sshpass -p linux ssh -o StrictHostKeyChecking=no -p 2222 root@localhost crinit-ctl poweroff || true \
        sleep 5  \
    ",
    outs = [
        "ebcl-qemuarm64-deployed/fastdev-ubuntu-ebclfsa-ebcl-qemuarm64.wic",
        "ebcl-qemuarm64-deployed/fastdev-ubuntu-ebclfsa-ebcl-qemuarm64-vmlinux",
        "qemu_deployment.log",
    ],
    visibility = [
        "//visibility:public",
    ],
)
