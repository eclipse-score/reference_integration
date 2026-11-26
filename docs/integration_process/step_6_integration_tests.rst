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

Step 6 — Add integration tests
==============================

.. admonition:: What it unlocks
   :class: tip

   **Runtime verification** — Your module is **exercised at runtime**: on the
   deployed images and against its public API, not just built. This is the
   difference between "it ships" and "it provably works on the target".

Two levels of integration tests
-------------------------------

The integration has two complementary kinds of integration tests:

* **Platform integration tests (PIT) — does it run on the platform?**
  Black-box tests on the real images. They show that the integrated platform
  starts and runs end to end, and verify stakeholder requirements.
* **Feature integration tests (FIT) — does the feature behave correctly?**
  White-box tests against the module APIs. They check specific behaviour in
  depth and verify feature requirements.

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * -
     - Platform integration tests (PIT)
     - Feature integration tests (FIT)
   * - What runs
     - The module's showcase (Step 4) on a booted image, started through the
       showcase CLI; optional extra checks on console output, files or DLT
     - Scenario binaries written in Rust/C++ against the module's public API,
       driven by pytest
   * - Where
     - Linux x86_64 image (Docker) and QNX x86_64 image (QEMU), via ITF
     - Linux host
   * - Verifies
     - Stakeholder requirements (``stkh_req__…``)
     - Feature requirements (``feat_req__…``)
   * - Location
     - `platform_integration_tests/ <https://github.com/eclipse-score/reference_integration/tree/main/platform_integration_tests>`_
     - `feature_integration_tests/ <https://github.com/eclipse-score/reference_integration/tree/main/feature_integration_tests>`_
   * - Bazel target
     - ``//platform_integration_tests:pit``
     - ``//feature_integration_tests/test_cases:fit``

Platform integration tests
--------------------------

Add a package ``platform_integration_tests/<module>`` with a ``py_itf_test``
(copy an existing one, e.g. ``platform_integration_tests/time``) and list it in
the ``pit`` test suite in ``platform_integration_tests/BUILD``. The test runs your
showcase by its name from the ``*.score.json`` file and links the stakeholder
requirement it verifies:

.. code-block:: python

   from attribute_plugin import add_test_properties
   from showcase_runner import run_showcases

   @add_test_properties(
       partially_verifies=["stkh_req__my_area__my_requirement"],
       test_type="interface-test",
       derivation_technique="requirements-analysis",
   )
   def test_my_module_showcase(target):
       output = run_showcases(target, "My Module Example")
       assert "expected result" in output

``run_showcases`` fails the test if any app of the showcase exits non-zero or is
killed by a signal. Add your own checks on top where the exit code is not enough:
console output (``platform_integration_tests/platform_info``), files on the target
(``platform_integration_tests/persistency``) or recorded DLT traffic
(``platform_integration_tests/platform_run``).

The PITs run for the Linux image in
`test_and_docs.yml <https://github.com/eclipse-score/reference_integration/blob/main/.github/workflows/test_and_docs.yml>`_
and for the QNX image in
`build_and_test_qnx.yml <https://github.com/eclipse-score/reference_integration/blob/main/.github/workflows/build_and_test_qnx.yml>`_:

.. code-block:: bash

   # Linux x86_64 image (Docker)
   bazel test --config=linux-x86_64 //platform_integration_tests:pit
   # QNX image, booted under QEMU
   bazel test --config=itf-qnx-x86_64 //platform_integration_tests:pit

Feature integration tests
-------------------------

Implement scenarios for your feature in Rust or C++ under
``feature_integration_tests/test_scenarios`` and the pytest cases that run them
under ``feature_integration_tests/test_cases/tests/<feature>``. Each test links
the feature requirement it verifies with ``add_test_properties``. The FITs run in
``test_and_docs.yml`` on the Linux host:

.. code-block:: bash

   bazel test --config=linux-x86_64 //feature_integration_tests/test_cases:fit

.. note::

   **Planned consolidation.** The FITs run only on the Linux host and the PITs
   only on the Linux x86_64 and QNX x86_64 images. Both should run against **all
   four target images** (Linux x86_64, QNX, AutoSD, EBcLfSA aarch64).
