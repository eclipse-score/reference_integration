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

Step 6 — Add feature integration tests
======================================

.. admonition:: What it unlocks
   :class: tip

   **Runtime feature tests** — Your showcase is **exercised at runtime** on the
   deployed images, not just built. This is the difference between "it ships"
   and "it provably works on the target".

Two test frameworks
-------------------

The integration currently uses **two** separate frameworks for integration
tests, each driven by its own Bazel target and run in a different CI workflow:

* **FIT — scenario-based feature integration tests**
  (`feature_integration_tests/test_cases <https://github.com/eclipse-score/reference_integration/tree/main/feature_integration_tests/test_cases>`_,
  target ``//feature_integration_tests/test_cases:fit``). Python/Pytest test
  cases that orchestrate Rust and C++ scenarios. They are executed as part of the
  ``test_and_docs`` workflow on the default Linux platform:

  .. code-block:: bash

     bazel test --config=linux-x86_64 //feature_integration_tests/test_cases:fit

* **ITF — Integration Test Framework**
  (`feature_integration_tests/itf <https://github.com/eclipse-score/reference_integration/tree/main/feature_integration_tests/itf>`_,
  target ``//feature_integration_tests/itf``). Black-box tests that run against a
  booted image. They are executed for **two** images only — QNX (on QEMU) by
  `build_and_test_qnx.yml <https://github.com/eclipse-score/reference_integration/blob/main/.github/workflows/build_and_test_qnx.yml>`_ and
  Linux x86_64 by
  `build_and_test_linux.yml <https://github.com/eclipse-score/reference_integration/blob/main/.github/workflows/build_and_test_linux.yml>`_:

  .. code-block:: bash

     # QNX image, booted under QEMU
     bazel test --config=itf-qnx-x86_64 //feature_integration_tests/itf
     # Linux x86_64 image
     bazel test --config=linux-x86_64  //feature_integration_tests/itf

Add black-box tests that exercise your showcase on a running target under
`feature_integration_tests/itf <https://github.com/eclipse-score/reference_integration/tree/main/feature_integration_tests/itf>`_. They run
against the deployed image and assert that the binary is present and behaves as
expected:

.. code-block:: python

   def test_my_example_is_deployed(target):
       exit_code, _ = target.execute("test -f /showcases/bin/my_example")
       assert exit_code == 0

   def test_my_example_runs(target):
       exit_code, out = target.execute("/showcases/bin/my_example")
       assert exit_code == 0

The existing ``test_run_all_showcases`` test invokes ``cli --examples=all``, so
any showcase you registered in Step 4 is already covered by the end-to-end run.

.. note::

   **Planned consolidation.** Having two integration-test frameworks (FIT and
   ITF) executed by different workflows on different platforms is a known gap.
   The execution should be consolidated so that **all integration tests — both
   FIT and ITF — run against all four target images** (Linux x86_64, QNX, AutoSD,
   EBcLfSA aarch64), instead of FIT running only in ``test_and_docs`` on Linux
   and ITF running only for the QNX and Linux images.
