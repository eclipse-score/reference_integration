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
load("@rules_python//python:defs.bzl", "py_binary", "py_library")
load("@score_tooling//python_basics:defs.bzl", "score_py_pytest")

py_library(
    name = "profile",
    srcs = [
        "__init__.py",
        "tools/__init__.py",
        "tools/profile.py",
    ],
    visibility = ["//visibility:public"],
)

py_library(
    name = "needs_export",
    srcs = ["tools/export_needs.py"],
    visibility = ["//visibility:public"],
    deps = [":profile"],
)

py_library(
    name = "receiver",
    srcs = ["tools/receive_srac.py"],
    visibility = ["//visibility:public"],
    deps = [":profile"],
)

py_binary(
    name = "enrich_sbom",
    srcs = ["tools/enrich_sbom.py"],
    main = "tools/enrich_sbom.py",
    visibility = ["//visibility:public"],
    deps = [":profile"],
)

py_binary(
    name = "export_needs",
    srcs = ["tools/export_needs_cli.py"],
    main = "tools/export_needs_cli.py",
    visibility = ["//visibility:public"],
    deps = [":needs_export"],
)

py_binary(
    name = "receive_srac",
    srcs = ["tools/receive_srac.py"],
    main = "tools/receive_srac.py",
    visibility = ["//visibility:public"],
    deps = [":profile"],
)

score_py_pytest(
    name = "srac_tests",
    srcs = glob(["tests/**/*.py"]),
    data = [
        "examples/generated/communication.cdx.json",
        "examples/generated/communication.sbom-reference.json",
        "examples/generated/communication.spdx.json",
        "examples/generated/communication.srac.json",
        "examples/lifecycle-health-monitor.srac.json",
        "examples/needs/communication.export.json",
        "examples/needs/communication.needs.json",
        "examples/persistency-kvs.srac.json",
        "examples/synthetic-safety-related.srac.json",
        "pilot/lifecycle-health-monitor/output/current-product.srac-report.json",
        "pilot/lifecycle-health-monitor/output/current-product.srac-report.sha256",
        "pilot/lifecycle-health-monitor/provenance.json",
        "pilot/lifecycle-health-monitor/safety-assessment-draft.md",
        "pilot/persistency-kvs/evidence-metrics.json",
        "pilot/persistency-kvs/input/reference-integration.spdx.json",
        "pilot/persistency-kvs/output/persistency-kvs.srac-report.json",
        "pilot/persistency-kvs/output/persistency-kvs.srac-report.sha256",
        "pilot/persistency-kvs/provenance.json",
        "pilot/persistency-kvs/requirements-traceability.md",
        "schema/srac.schema.json",
        "schema/srac-report.schema.json",
        "//:known_good.json",
    ],
    pytest_config = "//:pyproject.toml",
    deps = [
        ":needs_export",
        ":profile",
        ":receiver",
    ],
)

exports_files([
    "examples/lifecycle-health-monitor.srac.json",
    "examples/persistency-kvs.srac.json",
    "examples/synthetic-safety-related.srac.json",
    "examples/needs/communication.export.json",
    "examples/needs/communication.needs.json",
    "examples/generated/communication.sbom-reference.json",
    "examples/generated/communication.cdx.json",
    "examples/generated/communication.spdx.json",
    "examples/generated/communication.srac.json",
    "pilot/lifecycle-health-monitor/output/current-product.srac-report.json",
    "pilot/lifecycle-health-monitor/output/current-product.srac-report.sha256",
    "pilot/lifecycle-health-monitor/provenance.json",
    "pilot/lifecycle-health-monitor/safety-assessment-draft.md",
    "pilot/persistency-kvs/evidence-metrics.json",
    "pilot/persistency-kvs/input/reference-integration.spdx.json",
    "pilot/persistency-kvs/output/persistency-kvs.srac-report.json",
    "pilot/persistency-kvs/output/persistency-kvs.srac-report.sha256",
    "pilot/persistency-kvs/requirements-traceability.md",
    "schema/srac-report.schema.json",
    "schema/srac.schema.json",
])
