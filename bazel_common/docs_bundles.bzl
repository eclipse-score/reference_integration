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

# Generated from known_good.json at 2026-08-28T09:19:12Z
# Do not edit manually - use scripts/known_good/update_module_from_known_good.py --known known_good.json --output-dir-modules bazel_common

# Documentation bundle mounts for the docs() macro in the root BUILD file.
DOCS_BUNDLES = [
    {
        "bundle": "@score_baselibs//:docs_bundle",
        "mount_at": "modules/score_baselibs",
    },
    {
        "bundle": "@score_persistency//:docs_bundle",
        "mount_at": "modules/score_persistency",
    },
    {
        "bundle": "@score_kyron//:docs_bundle",
        "mount_at": "modules/score_kyron",
    },
    {
        "bundle": "@score_lifecycle//:docs_bundle",
        "mount_at": "modules/score_lifecycle",
    },
    {
        "bundle": "@score_logging//:docs_bundle",
        "mount_at": "modules/score_logging",
    },
    {
        "bundle": "@score_itf//:docs_bundle",
        "mount_at": "process_methods_tools/score_itf",
    },
    {
        "bundle": "@score_platform//:docs_bundle",
        "mount_at": "process_methods_tools/score_platform",
    },
    {
        "bundle": "@score_docs_as_code//:docs_bundle",
        "mount_at": "process_methods_tools/score_docs_as_code",
    },
    {
        "bundle": "@score_process_description//:docs_bundle",
        "mount_at": "process_methods_tools/score_process_description",
    },
]
