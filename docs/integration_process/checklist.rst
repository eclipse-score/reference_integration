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

Checklist
=========

Use this as a final review before opening your pull request:

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Step
     - Done when…
   * - 1 · Add module (register, regenerate, patches)
     - module entry added under ``modules.target_sw`` with ``repo`` + ``hash``;
       ``update_module_from_known_good.py`` ran and generated files committed;
       patches referenced if needed; ``known_good_correct`` and ``bzlmod-lock``
       checks green.
   * - 2 · Documentation
     - ``needs_json`` added to ``//:docs`` data and toctree entry in
       ``sw_components.rst``; ``//:docs_combo`` shows the module.
   * - 3 · Unit tests (default platform)
     - module compiles and unit tests pass on ``--config=linux-x86_64`` via
       ``quality_runners.py``; ``metadata`` tuned if needed.
   * - 4 · Platforms (build & test)
     - ``score_pkg_bundle`` + ``*.score.json`` added and registered in
       ``showcases/BUILD`` (ships into every image); ``bazel test
       @score_my_module//...`` passes.
   * - 5 · Component tests
     - *not available yet — to be introduced.*
   * - 6 · Integration tests
     - tests added under ``feature_integration_tests/itf``.
   * - 7 · Reporting
     - Rust coverage generated; verification/status tables updated.
   * - 8 · Code quality
     - formatting, Bazel Clippy (Rust) and the CodeQL/MISRA C++ scan pass.
