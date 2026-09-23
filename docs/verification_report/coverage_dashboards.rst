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

.. _coverage_dashboards:

Code Coverage Dashboards
========================

This page provides direct access to the detailed, interactive code coverage dashboards generated during continuous integration (CI) test execution.

Overview
--------

Code coverage analysis is performed across all target software modules enrolled in the reference integration, covering both C++ (via ``genhtml`` / lcov) and Rust (via Ferrocene / Blanket) implementations.

* **Summary Table:** See :doc:`Coverage Analysis Summary <coverage_summary>` for overall percentage numbers.
* **Platform Verification:** See :doc:`Platform Verification Report <platform_verification_report>`.

Project-Level Coverage Overview
-------------------------------

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Scope
     - Description & Link
   * - **All Modules Coverage Portal**
     - `Central Coverage Portal <../coverage/index.html>`_ — Consolidated view of all module dashboards generated in this build.

Component-Level Coverage Dashboards (C++)
-----------------------------------------

The following C++ modules are instrumented with lcov/gcov, generating interactive line, function, and branch coverage reports:

.. list-table::
   :header-rows: 1
   :widths: 30 20 50

   * - Module
     - Language
     - Interactive Dashboard Link
   * - ``score_baselibs``
     - C++
     - `Baselibs C++ Dashboard <../coverage/cpp/score_baselibs/index.html>`_
   * - ``score_communication``
     - C++
     - `Communication C++ Dashboard <../coverage/cpp/score_communication/index.html>`_
   * - ``score_config_management``
     - C++
     - `Config Management C++ Dashboard <../coverage/cpp/score_config_management/index.html>`_
   * - ``score_lifecycle``
     - C++
     - `Lifecycle C++ Dashboard <../coverage/cpp/score_lifecycle/index.html>`_
   * - ``score_logging``
     - C++
     - `Logging C++ Dashboard <../coverage/cpp/score_logging/index.html>`_
   * - ``score_persistency``
     - C++
     - `Persistency C++ Dashboard <../coverage/cpp/score_persistency/index.html>`_
   * - ``score_time``
     - C++
     - `Time C++ Dashboard <../coverage/cpp/score_time/index.html>`_

Component-Level Coverage Dashboards (Rust)
------------------------------------------

The following Rust modules are instrumented via Ferrocene LLVM source-based code coverage and rendered with Blanket:

.. list-table::
   :header-rows: 1
   :widths: 30 20 50

   * - Module
     - Language
     - Interactive Dashboard Link
   * - ``score_kyron``
     - Rust
     - `Kyron Rust Dashboard <../coverage/rust/score_kyron/index.html>`_
   * - ``score_lifecycle``
     - Rust
     - `Lifecycle Rust Dashboard <../coverage/rust/score_lifecycle/index.html>`_
   * - ``score_logging``
     - Rust
     - `Logging Rust Dashboard <../coverage/rust/score_logging/index.html>`_
   * - ``score_persistency``
     - Rust
     - `Persistency Rust Dashboard <../coverage/rust/score_persistency/index.html>`_

Coverage Metrics Interpretation
-------------------------------

* **Line Coverage:** The percentage of executable code statements executed by unit and component tests.
* **Function Coverage:** The percentage of declared functions or methods called at least once during execution.
* **Branch Coverage:** The percentage of decision points (conditional branches) where each branch was evaluated to true and false.
