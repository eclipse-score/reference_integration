..
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

Reference Integration Documentation
===================================

The **Reference Integration** is the central integration repository of the
eclipse-score project. It combines all
S-CORE software modules — including Communication, Logging, Orchestrator,
Persistency, Time, Config Management, Lifecycle, and Security/Crypto — into a
single, consistently versioned workspace.

Its purpose is to verify that all modules build, integrate, and pass their
tests together, providing a stable baseline for downstream projects. The
repository also hosts the consolidated documentation, verification reports,
and release notes for each S-CORE release.

Beyond validation, the **Reference Integration** also serves as a technical
blueprint for future commercial distributions. It demonstrates how S-CORE
modules can be combined into a coherent, releaseable platform baseline,
including the expected integration structure, verification artifacts, and
documentation set that downstream product distributions can build on.

.. grid:: 1 1 3 3
   :gutter: 3

   .. grid-item-card:: 📊 Status & Roadmap
      :link: s_core_v_1/index
      :link-type: doc

      :doc:`S-Core v1.0 Roadmap <s_core_v_1/roadmap/roadmap>` and PI planning.

   .. grid-item-card:: 📖 Process, Methods & Tools
      :link: process_methods_tools
      :link-type: doc

      S-CORE process description, platform standards, and documentation toolchain.

   .. grid-item-card:: ✅ Code Quality
      :link: verification_report/platform_verification_report
      :link-type: doc

      Platform verification report and test coverage results.

   .. grid-item-card:: Integration
      Reference Integration workflow and health overview with links to
      :doc:`Integration Process <integration_process/integration_process>` and
      `Integration Status <https://eclipse-score.github.io/reference_integration/main/status_dashboard.html>`_.

   .. grid-item-card:: Modules
      :link: sw_components
      :link-type: doc

      Central overview for all integrated modules. See :doc:`All Modules <sw_components>`.

   .. grid-item-card:: 📝 Release Notes
      :link: s_core_v_1/releases/releases
      :link-type: doc

      Overview of published S-CORE releases and their release notes.

.. toctree::
   :hidden:

   sw_components
   integration_process/integration_process
   process_methods_tools
   s_core_v_1/releases/releases
