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
  each tracked issue must have the **component** set and the **milestone** set
- Complete feature and component architecture for all modules (no open TBDs, status ``valid``)
- Fill in and approve ``chklst_arc_inspection.rst`` for all modules and features — each checklist point
  is either completed or the finding is noted in the checklist with a tracked issue;
  each tracked issue must have the **component** set and the **milestone** set
- All requirements relevant for v1.0 must be explicitly marked as such
- Implementation of functionality must be planned via tickets in the
  `main S-CORE GitHub project <https://github.com/orgs/eclipse-score/projects>`__ —
  each ticket must have the **component** set and the **milestone** set
- A Module Verification Report must be created for every module, tracking at minimum
  that unit-test coverage (C0/C1) reaches at least **90%** and dynamic code analysis
  (sanitizers: ASan/UBSan/LSan, TSan) passes with **0 findings**

Current State
-------------

See the relevant tables in :doc:`overall_status`:

- :ref:`overall_status_pa2` — Requirements Engineering
- :ref:`overall_status_pa3` — Architecture Design
- :ref:`overall_status_pa5` — Verification / Coverage

Feasibility Check
-----------------

Do we have everything in place to deliver the Release Gate v0.8 focus items?

**Tooling & Process**

- [ ] The S-CORE process templates (requirement, architecture, inspection checklists) are finalised and available
- [ ] sphinx-needs / docs-as-code toolchain supports the required requirement types and attributes
- [ ] CI pipeline enforces ``valid`` status and broken-link checks on requirements and architecture documents

**Inputs & Dependencies**

- [ ] Stakeholder requirements are stable enough to derive component requirements (no major scope changes expected)
- [ ] Inter-module interfaces are sufficiently defined to allow architecture sign-off
- [ ] External dependencies (e.g. AUTOSAR, SOME/IP specs) needed for requirements are accessible

**Definition of Done clarity**

- [ ] Acceptance criteria for "requirements complete" and "architecture complete" are agreed upon by all module owners
- [ ] It is clear what "no open TBDs" means — a shared definition exists

**Verification — how do we ensure it was done?**

- [ ] Every module's ``chklst_req_inspection.rst`` and ``chklst_arc_inspection.rst`` are reviewed and merged into the module repo
- [ ] The overall status tracker (``overall_status.rst``) reflects the current state for each module
- [ ] All tracked findings from inspections have a linked GitHub issue with component + milestone set
- [ ] A final Release Gate v0.8 review meeting confirms sign-off by module owners and process responsible

**Integration in Reference Integration**

- [ ] All modules with completed requirements and architecture are integrated in this reference integration repository
- [ ] The reference integration build passes (no broken imports, no unresolved need IDs)
- [ ] The documentation (this site) builds without warnings for all Release Gate v0.8 modules
- [ ] The Release Gate v0.8 status table in ``overall_status.rst`` is updated to reflect the final state
