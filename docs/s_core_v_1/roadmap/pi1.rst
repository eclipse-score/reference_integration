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

🚀 Release Gate v0.8 — 13 May – 13 July 2026
=================================================

Milestone: `score/v0.8 <https://github.com/eclipse-score/score/milestone/30>`__

Focus: Requirements Engineering (PA2) + Architecture Design (PA3)
------------------------------------------------------------------

- Complete feature and component requirements for all modules (no open TBDs, status ``valid``)
- Fill in and approve ``chklst_req_inspection.rst`` for all modules and features — each checklist point
  is either completed or the finding is noted in the checklist with a tracked issue;
  each tracked issue must have the **team** set and the **milestone** set
- Complete feature and component architecture for all modules (no open TBDs, status ``valid``)
- Fill in and approve ``chklst_arc_inspection.rst`` for all modules and features — each checklist point
  is either completed or the finding is noted in the checklist with a tracked issue;
  each tracked issue must have the **team** set and the **milestone** set
- All requirements relevant for v1.0 must be explicitly marked as such
- Implementation of functionality must be planned via tickets in the
  `main S-CORE GitHub project <https://github.com/orgs/eclipse-score/projects>`__ —
  each ticket must have the **team** set and the **milestone** set
- A Module Verification Report must be created for every module, tracking at minimum
  that unit-test coverage (C0/C1) reaches at least **90%** and dynamic code analysis
  (sanitizers: ASan/UBSan/LSan, TSan) passes with **0 findings**

Current State
-------------

See the relevant tables in :doc:`overall_status`:

- :ref:`overall_status_pa2` — Requirements Engineering
- :ref:`overall_status_pa3` — Architecture Design
- :ref:`overall_status_pa5` — Verification / Coverage

Work Breakdown
--------------

- Mark every **feature requirement** that is in scope for v1.0 with the
  `valid_from <https://github.com/eclipse-score/docs-as-code/blob/main/src/extensions/score_metamodel/metamodel.yaml>`__
  attribute, set to one of the predefined release versions: ``v0.5``,
  ``v0.7``, ``v0.8``, ``v0.9``, ``v0.10`` or ``v1.0`` (semantics: see
  `tool_req__docs_req_attr_validity_correctness
  <https://github.com/eclipse-score/docs-as-code/blob/main/docs/internals/requirements/requirements.rst>`__).
  Only feature requirements with ``valid_from`` set are considered relevant
  for v1.0; together with **all elements linked to them** — component
  requirements, AoUs, feature architecture and component architecture — they
  form the v1.0 scope and are the only elements counted in the roadmap
  statistics.
- All in-scope feature requirements and the elements linked to them
  (component requirements, AoUs, feature architecture, component architecture)
  are in status ``valid``.
- Implement all missing automation checks for requirement and architecture
  elements as part of the docs-as-code toolchain used for generation of the
  documentation (``//:docs``), as depicted in the *Process Status* pies on
  :doc:`overall_status` (PA2 / PA3 *Req. verification status*)
- Provide a standardized CI/CD workflow for all implementation modules to
  validate requirements and architecture artifacts in compliance with the
  S-CORE process. The workflow shall be executed in the
  ``reference_integration`` repository to verify, across all integrated
  modules, that the artifacts conform to the defined process and that the
  resulting documentation can be successfully generated.
- Create and fully complete the inspection checklists for requirements and
  architecture. All findings shall be documented as tickets assigned to a
  milestone less than or equal to ``v1.0``, with the corresponding
  **team** attribute set and the **process area** set to ``pa2_req_eng``
  (for requirement findings) or ``pa3_arch_design`` (for architecture
  findings) respectively. Any alternative approach to the inspection
  checklists must first be agreed upon with the process community, and the
  decision must be documented.
- All outstanding implementations of requirements relevant for ``v1.0``
  shall be tracked by tickets. Each ticket must be assigned to a milestone
  less than or equal to ``v1.0``, have the dedicated **team** attribute set,
  and have its **process area** set to ``pa4_impl``.
- Create and fully complete the Module Verification Report for every
  module. All findings shall be documented as tickets assigned to a
  milestone less than or equal to ``v1.0``, with the corresponding
  **team** attribute set and the **process area** set to
  ``pa5_verification``.
