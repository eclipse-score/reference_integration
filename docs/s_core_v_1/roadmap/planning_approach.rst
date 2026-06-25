..
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

:hide-toc:

.. _v1_0_planning_approach:

Planning Approach
=================

.. note::

   This page is **a short summary** of how the S-CORE v1.0 roadmap is
   planned. The authoritative planning procedure — covering project
   management, release management, change management and the underlying
   governance — is described in the
   `Platform Management Plan
   <https://eclipse-score.github.io/score/main/platform_management_plan/index.html>`__
   (in particular
   `Project Management
   <https://eclipse-score.github.io/score/main/platform_management_plan/project_management.html>`__
   and
   `Release Management
   <https://eclipse-score.github.io/score/main/platform_management_plan/release_management.html>`__).

Where we plan
-------------

All v1.0 planning is tracked in the central GitHub project
`S-CORE v1.0 Planning <https://github.com/orgs/eclipse-score/projects/17/views/37>`__.
This project is the single source of truth for the roadmap; the figures and
tables shown elsewhere in this section are derived from it.

Product Increments per Feature Team / Community
-----------------------------------------------

Every Feature Team and every Community creates **one ticket of type
"Product Increment"** for each release gate they contribute to. This ticket:

- is the **main ticket** for the team's work in that release gate,
- is **mapped to the corresponding milestone** (using the ticket's
  *milestone* attribute) in the
  `eclipse-score/score milestones
  <https://github.com/eclipse-score/score/milestones>`__ (e.g. ``v0.8``,
  ``v0.9``, ``v0.10``, ``v1.0``), and
- represents the team's commitment for that release gate.

Sub-tickets — the actual work
-----------------------------

All work the team performs for the corresponding milestone / release gate is
**linked as sub-tickets under the Product Increment ticket**.

- The breakdown does **not need to be exhaustive**; it can be detailed if a
  team wants to, but at a minimum it should reflect the **main achievements
  or work packages** planned for that release gate.
- The sub-ticket structure ensures that the Product Increment ticket gives a
  meaningful overview of the team's scope without having to dig through every
  individual issue.

Process-area attribute
----------------------

Wherever possible, each sub-ticket sets the **process area** GitHub project's
attribute, for
example ``pa1_req_eng``, ``pa2_arch_design``, ``pa3_implementation``,
``pa4_verification``. This makes it possible to group and filter tickets not
only **by time** (milestone / release gate) but also **by function**
(process area), which is what feeds the per-process-area views on the
:doc:`Overall Status <overall_status>` page.

Terminology
-----------

To keep the planning vocabulary unambiguous, the following terms are used
consistently throughout this section:

- **Version** — A *version* refers to a software product version in the
  classical sense: a defined, released state of the S-CORE platform with a
  fixed scope and quality (e.g. ``v0.5``, ``v1.0``). It is the unit that is
  shipped to and consumed by users of the platform.
- **Release / Milestone** — A *release* (also called *milestone*, mapped
  one-to-one to a `GitHub milestone
  <https://github.com/eclipse-score/score/milestones>`__) is a planning
  checkpoint that we use to **track our work on the way to a version**.
  Several releases / milestones (e.g. ``v0.8``, ``v0.9``, ``v0.10``)
  typically lead up to a single version (``v1.0``).
- **Release Gate** — A *release gate* is the set of deliverables that, by
  the corresponding release / milestone, **must be done for sure** in order
  to keep the path to the target version on track. The release gate
  documents the **mandatory minimum**; it does **not** restrict the teams
  to working only on the items listed there. Teams are free to work on
  additional topics in parallel — the release gate simply makes explicit
  what is non-negotiable for that milestone.

