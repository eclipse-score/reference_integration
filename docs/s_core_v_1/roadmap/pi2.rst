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

Release Gate v0.9 — 14 July – 7 September 2026
==============================================

Milestone: `score/v0.9 <https://github.com/eclipse-score/score/milestone/31>`__

**Focus: Implementation (PA4)**

- A Module Verification Report must be extended for every module, showing at least **75%**
  **component requirement test coverage** (linked via ``FullyVerifies`` / ``PartiallyVerifies``
  on ``comp_req__...`` IDs in unit tests and component integration tests)
- A Platform Verification Report must be created, showing at least **75%**
  **feature requirement test coverage** (linked via ``FullyVerifies`` / ``PartiallyVerifies``
  on ``feat_req__...`` IDs in Feature Integration Tests)
- Detailed design documented for all modules (no open TBDs, status ``valid``)
- Fill in and approve ``chklst_impl_inspection.rst`` for all modules — each checklist point
  is either completed or the finding is noted in the checklist with a tracked issue
- Remaining requirements (the ~20%) must have tracked tickets in the
  `main S-CORE GitHub project <https://github.com/orgs/eclipse-score/projects>`__ —
  each ticket must have the **component** set and the **milestone** set

**Current State**

See the relevant tables in :doc:`overall_status`:

- :ref:`overall_status_pa4` — Implementation
- :ref:`overall_status_pa5` — Verification / Coverage
