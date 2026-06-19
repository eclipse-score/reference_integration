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

.. _reporting:

Step 7 — Add coverage and verification reports
==============================================

.. admonition:: What it unlocks
   :class: tip

   **Consolidated reports** — Your module shows up in the **consolidated
   coverage and verification / status reports** that are published alongside the
   docs — the evidence side of the integration.

.. note::

   **No extra action is required here.** As already explained in
   :doc:`Step 3 <step_3_unit_tests>`, the ``test_and_docs`` workflow already
   executes your module's unit tests and gathers and publishes the code-coverage
   data. If your module passes Step 3, it is automatically part of the reports
   described below — this chapter only explains *how* that collection,
   aggregation and publishing happens.

How coverage is collected
-------------------------

The ``test_and_docs`` workflow runs
`scripts/quality_runners.py <https://github.com/eclipse-score/reference_integration/blob/main/scripts/quality_runners.py>`_, which iterates
over **every** module under ``modules.target_sw`` in ``known_good.json`` and, per
module, runs its unit tests with coverage (``bazel coverage``) and then extracts
a per-language summary. The driver is the module's ``metadata.langs``:

* ``"cpp"`` → a C++ (lcov/genhtml) coverage run.
* ``"rust"`` → a Rust coverage run.

Both write into the two consolidated reports
`docs/verification_report/unit_test_summary.md <https://github.com/eclipse-score/reference_integration/blob/main/docs/verification_report/unit_test_summary.md>`_
and
`docs/verification_report/coverage_summary.md <https://github.com/eclipse-score/reference_integration/blob/main/docs/verification_report/coverage_summary.md>`_.
The same scoping metadata applies to both languages:

* ``metadata.code_root_path`` — the target pattern that is instrumented and
  tested (``@score_my_module<code_root_path>``).
* ``metadata.extra_test_config`` — extra ``--flag`` settings for the coverage run.
* ``metadata.exclude_test_targets`` — targets excluded from the run.

So for most modules **no extra wiring is needed** — declaring the language in
``metadata.langs`` (Step 1) is what enrolls the module into coverage.

Where the results are exported
------------------------------

``quality_runners.py`` does not only run the tests and coverage — it parses the
output per module and **exports the results** in three forms:

* **Markdown summaries committed into the docs.** A unit-test execution table
  and a coverage table are written to
  `docs/verification_report/unit_test_summary.md <https://github.com/eclipse-score/reference_integration/blob/main/docs/verification_report/unit_test_summary.md>`_
  (columns: module, passed, failed, skipped, total) and
  `docs/verification_report/coverage_summary.md <https://github.com/eclipse-score/reference_integration/blob/main/docs/verification_report/coverage_summary.md>`_
  (columns: module, lines, functions, branches). These two files are pulled into
  the published documentation by
  `docs/verification_report/platform_verification_report.rst <https://github.com/eclipse-score/reference_integration/blob/main/docs/verification_report/platform_verification_report.rst>`_,
  so every module's unit-test and coverage numbers appear in the
  **Platform Verification Report** on the docs site.
* **Detailed HTML coverage reports.** The per-module ``genhtml`` / Rust coverage
  HTML is written under the coverage output directory
  (``artifacts/coverage/cpp/<module>`` and ``artifacts/coverage/rust/<module>``
  by default; override with ``--coverage-output-dir``).
* **CI job summary.** In CI the ``test_and_docs`` workflow additionally appends
  the two markdown summaries to the GitHub Actions **job summary**
  (``$GITHUB_STEP_SUMMARY``), so the pass/fail and coverage tables are visible
  directly on the workflow run.

C++ coverage
------------

If your module declares ``cpp`` in ``metadata.langs``, ``quality_runners.py``
runs ``bazel coverage`` over ``@score_my_module<code_root_path>`` and produces an
HTML/lcov report via ``genhtml`` (the ``lcov`` package must be present — CI
installs it; locally ``sudo apt-get install -y lcov``). The line/function/branch
numbers land in ``coverage_summary.md``. To make your module's C++ coverage
meaningful:

#. Ensure ``metadata.langs`` contains ``"cpp"`` and ``metadata.code_root_path``
   points at the instrumented source root.
#. Use ``metadata.exclude_test_targets`` to drop tests that should not count
   (e.g. examples, flaky or environment-specific targets).
#. Reproduce a single module's run locally with:

   .. code-block:: bash

      python3 scripts/quality_runners.py --modules-to-test score_my_module

Rust coverage
-------------

If your module declares ``rust`` in ``metadata.langs``, the
``rust_coverage_report`` target is generated automatically into
`rust_coverage/BUILD <https://github.com/eclipse-score/reference_integration/blob/main/rust_coverage/BUILD>`_ by step 1.2 — no manual action
is needed. Tune ``metadata.exclude_test_targets`` and
``metadata.rust_coverage_config`` in ``known_good.json`` to control what is
measured. Build a single module's report with:

.. code-block:: bash

   bazel run //rust_coverage:rust_coverage_score_my_module

Verification & status reports
-----------------------------

The consolidated reports live under
`docs/verification_report <https://github.com/eclipse-score/reference_integration/tree/main/docs/verification_report>`_ and the roadmap /
status trackers under
`docs/s_core_v_1/roadmap <https://github.com/eclipse-score/reference_integration/tree/main/docs/s_core_v_1/roadmap>`_ (e.g.
``overall_status.rst``). Add your module to the relevant tables/rows so it shows
up in the platform verification report and the feature/process status overview.
The full catalogue of reports is under :ref:`reports`.
