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

.. _v1_0_release_plan:

S-CORE v1.0 Roadmap
====================

This document describes the release planning for **S-CORE v1.0**, organized around the
`eclipse-score/score milestones <https://github.com/eclipse-score/score/milestones>`__,
and covers **two overarching project goals**:

Feature Completeness
--------------------

Selected modules are fully implemented and tested.

.. image:: ../../_assets/sw_arch_v_1.drawio.svg
   :alt: S-CORE v1.0 Software Architecture
   :align: center
   :width: 100%

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Module
     - Notes
   * - `Baselibs <https://github.com/eclipse-score/baselibs>`__
     - Base libraries (C++)
   * - `Baselibs Rust <https://github.com/eclipse-score/baselibs>`__
     - Base libraries (Rust)
   * - `Communication <https://github.com/eclipse-score/communication>`__
     - IPC / service-oriented communication
   * - `Logging <https://github.com/eclipse-score/logging>`__
     - Platform logging
   * - `Persistency <https://github.com/eclipse-score/persistency>`__
     - Data persistence
   * - `Time <https://github.com/eclipse-score/inc_time>`__
     - Time services
   * - `Config Management <https://github.com/eclipse-score/config_management>`__
     - Configuration management
   * - `Lifecycle <https://github.com/eclipse-score/lifecycle>`__
     - Lifecycle management
   * - `Security/Crypto <https://github.com/eclipse-score/inc_security_crypto>`__
     - Cryptographic services
   * - `Diagnosis <https://github.com/eclipse-score/inc_diagnosis>`__
     - On-board diagnostics / DTC management
   * - `NM <https://github.com/eclipse-score/inc_nm>`__
     - Network management
   * - `Some/IP <https://github.com/eclipse-score/someip>`__
     - SOME/IP communication middleware

Qualifiable State
-----------------

All modules follow the S-CORE process and use S-CORE tools for
artifact generation across the following process areas: **Requirements Engineering**, **Architecture Design**, **Implementation**, **Verification**.

Management
^^^^^^^^^^

.. grid:: 2 4 4 4
   :class-container: score-grid score-grid-compact
   :gutter: 4

   .. grid-item-card:: `Platform Management <https://eclipse-score.github.io/process_description/main/process_areas/platform_management/index.html>`__
      :class-card: card-pa-grey

      Manage the common platform, its modules and integration.

   .. grid-item-card:: `Safety Management <https://eclipse-score.github.io/process_description/main/process_areas/safety_management/index.html>`__
      :class-card: card-pa-grey

      Plan and oversee safety activities across the project lifecycle.

   .. grid-item-card:: `Security Management <https://eclipse-score.github.io/process_description/main/process_areas/security_management/index.html>`__
      :class-card: card-pa-grey

      Plan and oversee cybersecurity activities across the project lifecycle.

   .. grid-item-card:: `Quality Management <https://eclipse-score.github.io/process_description/main/process_areas/quality_management/index.html>`__
      :class-card: card-pa-grey

      Define and monitor quality objectives, measures and improvements.

   .. grid-item-card:: `Change Management <https://eclipse-score.github.io/process_description/main/process_areas/change_management/index.html>`__
      :class-card: card-pa-grey

      Control and track changes to work products and configurations.

   .. grid-item-card:: `Problem Resolution <https://eclipse-score.github.io/process_description/main/process_areas/problem_resolution/index.html>`__
      :class-card: card-pa-grey

      Identify, analyse and resolve problems found during development.

   .. grid-item-card:: `Release Management <https://eclipse-score.github.io/process_description/main/process_areas/release_management/index.html>`__
      :class-card: card-pa-grey

      Plan, prepare and control the release of deliverables.

   .. grid-item-card:: `Process Management <https://eclipse-score.github.io/process_description/main/process_areas/process_management/index.html>`__
      :class-card: card-pa-grey

      Define, deploy and improve the organisational process.

Development
^^^^^^^^^^^

.. grid:: 1 2 3 4
   :class-container: score-grid
   :gutter: 4

   .. grid-item-card:: `Requirements Engineering <https://eclipse-score.github.io/process_description/main/process_areas/requirements_engineering/index.html>`__
      :class-card: card-pa-highlight

      Elicit, specify and manage stakeholder and system requirements.

   .. grid-item-card:: `Architecture Design <https://eclipse-score.github.io/process_description/main/process_areas/architecture_design/index.html>`__
      :class-card: card-pa-highlight

      Define and document the system and software architecture.

   .. grid-item-card:: `Implementation <https://eclipse-score.github.io/process_description/main/process_areas/implementation/index.html>`__
      :class-card: card-pa-highlight

      Develop and unit-test software units according to the design.

   .. grid-item-card:: `Verification <https://eclipse-score.github.io/process_description/main/process_areas/verification/index.html>`__
      :class-card: card-pa-highlight

      Verify that work products fulfil their specified requirements.

   .. grid-item-card:: `Safety Analysis <https://eclipse-score.github.io/process_description/main/process_areas/safety_analysis/index.html>`__
      :class-card: card-pa-highlight

      Identify and assess safety hazards and derive mitigation measures.

   .. grid-item-card:: `Security Analysis <https://eclipse-score.github.io/process_description/main/process_areas/security_analysis/index.html>`__
      :class-card: card-pa-grey

      Identify and assess security threats and derive mitigation measures.

Support
^^^^^^^

.. grid:: 1 2 3 4
   :class-container: score-grid
   :gutter: 4

   .. grid-item-card:: `Configuration Management <https://eclipse-score.github.io/process_description/main/process_areas/configuration_management/index.html>`__
      :class-card: card-pa-grey

      Control versions and baselines of all project artefacts.

   .. grid-item-card:: `Tool Management <https://eclipse-score.github.io/process_description/main/process_areas/tool_management/index.html>`__
      :class-card: card-pa-grey

      Qualify and manage tools used in the development process.

   .. grid-item-card:: `Documentation Management <https://eclipse-score.github.io/process_description/main/process_areas/documentation_management/index.html>`__
      :class-card: card-pa-grey

      Plan, create and maintain project and product documentation.

.. note::

   We will also work on the other process areas, but they are not in the main focus for S-CORE v1.0
   (shown grayed out above).

Status & Next Steps
-------------------

.. raw:: html
   :file: ../../_assets/pi_timeline_2026.drawio.svg

.. raw:: html

   <div style="margin-top: 2rem;"></div>

.. toctree::
   :titlesonly:
   :maxdepth: 1

   Overall Status <overall_status>
   Planning Approach <planning_approach>
   Release Gate v0.8 — Requirements Engineering + Architecture Design <pi1>
   Release Gate v0.9 — Implementation <pi2>
   Release Gate v0.10 — Verification <pi3>
   Release Gate v1.0 — Hardening & Release <pi4>

