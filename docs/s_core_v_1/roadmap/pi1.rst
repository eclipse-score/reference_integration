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
- The current state of every module — including its implementation — must be
  integrated into the ``reference_integration`` repository
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

  .. warning::

     **After the release of v0.8, every modification to requirements that are
     relevant for S-CORE v1.0 (i.e. carry a ``valid_from`` of ``v1.0`` or
     earlier and are still in the v1.0 scope) must be reviewed and approved
     in the TL circle** before it is merged.
- All in-scope feature requirements and the elements linked to them
  (component requirements, AoUs, feature architecture, component architecture)
  are in status ``valid``. The overall status can always be tracked on the
  :doc:`overall_status` page.
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

  - In analogy to the unified unit-test/coverage target, all modules must
    agree on a **single, unified Bazel target** that every module exposes
    for documentation generation and for the S-CORE process validation of
    requirements and architecture artifacts. This target shall be
    **agreed upon and documented** as a **public Bazel interface** that
    every implementation Bazel module is required to implement.
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
- Define the set of **target platforms** that S-CORE officially supports
  for v1.0. For every supported platform there shall be an **official
  toolchain**, and the ``reference_integration`` repository shall provide
  a dedicated CI/CD workflow that compiles every module against that
  platform's toolchain. Every implementation module must be **buildable
  with this toolchain**, and it is **strongly recommended** that each
  module reuses the same toolchain definition locally instead of
  maintaining its own. The supported platforms together with their
  official toolchains shall be **properly documented** so that every
  module owner can refer to a single authoritative source.
- Create and fully complete the Module Verification Report for every
  module. All findings shall be documented as tickets assigned to a
  milestone less than or equal to ``v1.0``, with the corresponding
  **team** attribute set and the **process area** set to
  ``pa5_verification``.

  - Define a standardized CI/CD workflow that runs the unit tests and
    measures the corresponding code coverage for every module, and
    integrate it into the ``reference_integration`` repository so that it
    is part of the **voting CI/CD pipeline**. All modules must agree on a
    **single, unified Bazel target** that every module exposes for
    invoking its unit tests and coverage measurement. This target shall
    be documented as a **public Bazel interface** that every
    implementation Bazel module is required to implement. Reuse and
    extend the existing rules where possible — see
    `eclipse-score/tooling — bazel/rules/rules_score
    <https://github.com/eclipse-score/tooling/tree/main/bazel/rules/rules_score>`__.
  - All unit tests shall be executed with **active sanitizers**
    (ASan/UBSan/LSan, TSan). The toolchain used to run the unit tests,
    measure coverage and enable the sanitizers shall be **agreed upon and
    unique** across all implementation modules — it is the same toolchain
    that is used in the ``reference_integration`` repository in the
    CI/CD workflow mentioned above. All implementation modules are
    strongly encouraged to use this toolchain **locally** as well, in
    addition to its execution in the CI/CD pipeline.
