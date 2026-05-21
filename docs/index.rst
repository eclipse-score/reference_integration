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

.. grid:: 1 1 3 3
   :gutter: 3

   .. grid-item-card:: 📊 Status & Roadmap
      :link: status_roadmap
      :link-type: doc

      Module status, :doc:`S-Core v1.0 Roadmap <s_core_v_1/roadmap/roadmap>`, PI planning, and integration status.

   .. grid-item-card:: 📖 Process, Methods & Tools
      :link: process_methods_tools
      :link-type: doc

      S-CORE process description, platform standards, and documentation toolchain.

   .. grid-item-card:: ✅ Code Quality
      :link: code_quality
      :link-type: doc

      Platform verification report and test coverage results.

.. toctree::
   :hidden:

   status_roadmap
   process_methods_tools
   code_quality
