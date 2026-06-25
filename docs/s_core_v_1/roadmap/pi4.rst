..
   # *******************************************************************************
   # Copyright (c) 2024 Contributors to the Eclipse Foundation
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

Release Gate v1.0 — 3 November – 15 December 2026
==================================================

Milestone: `score/v1.0 <https://github.com/eclipse-score/score/milestone/27>`__

**Focus: Hardening & Release**

- All inspection checklists are ``valid`` and complete for all v1.0-relevant features and modules:

  - ``chklst_req_inspection.rst`` — Requirements Inspection
  - ``chklst_arc_inspection.rst`` — Architecture Inspection
  - ``chklst_impl_inspection.rst`` — Implementation Inspection
- All module verification reports (``wp__verification_module_ver_report``) are approved by a Committer, containing:

  - **Requirements coverage**: all ``valid`` component requirements are linked to at least one test
    via ``FullyVerifies`` / ``PartiallyVerifies`` — pass/fail verdict per requirement documented
  - **Architecture coverage**: all component architecture elements are linked to at least one test — verdict documented
  - **Structural coverage**: C0 (line) and C1 (branch) coverage per unit listed and meets targets
  - **Static code analysis**: 0 open ``Critical`` or ``High`` findings
  - **Dynamic code analysis**: 0 sanitizer findings (ASan/UBSan/LSan, TSan)
- The Platform Verification Report (``wp__verification_platform_ver_report``) is approved by a Committer, containing:

  - **Feature requirements coverage**: all ``valid`` feature requirements are linked to at least one
    Feature Integration Test via ``FullyVerifies`` / ``PartiallyVerifies`` — pass/fail verdict per requirement documented
  - **Feature architecture coverage**: all feature architecture elements are linked to at least one test — verdict documented
  - **Feature Integration Test results**: pass/fail/not_run result per test case documented
  - **Feature Integration Test logs**: test logs per test case attached
- Release notes and changelog for v1.0 finalised
