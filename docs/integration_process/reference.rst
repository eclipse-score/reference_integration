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

Reference
=========

This section is a catalogue of *what already exists* in the integration — the
CI checks that run on every change and the consolidated reports — together with
the touch-point a new module has in each. Use it to understand where your module
shows up once it is wired in via the steps above. The supported target platforms
and their images are listed in :ref:`supported_platforms` (Step 4).

.. _ci_checks:

CI checks
---------

The pipelines live under `.github/workflows <../../.github/workflows>`_. Most
operate on ``//...`` and pick up your module without changes; the table says
what each check verifies and whether you typically need to touch anything.

**Gating** marks the checks that run in the merge queue
(``merge_group``) and must therefore be green before a pull request can be
merged. The remaining checks are informational, run only on ``push``/schedule,
or gate a different event (release approvals). The definitive list of *required*
status checks is configured in the repository's GitHub branch-protection /
merge-queue settings; the column below reflects merge-queue participation
declared in the workflows.

.. list-table::
   :header-rows: 1
   :widths: 30 36 12 22

   * - Check (workflow)
     - What it verifies
     - Gating
     - Your action
   * - `build_and_test_qnx.yml <../../.github/workflows/build_and_test_qnx.yml>`_
     - Builds the QNX IFS and runs integration tests on QEMU.
     - **yes**
     - none (graph-wide)
   * - `build_and_test_autosd.yml <../../.github/workflows/build_and_test_autosd.yml>`_
     - Builds the AutoSD OCI image with the Automotive Image Builder.
     - **yes**
     - none (graph-wide)
   * - `build_and_test_ebclfsa.yml <../../.github/workflows/build_and_test_ebclfsa.yml>`_
     - Builds the EBcLfSA image and runs the high-integrity safety tests.
     - **yes**
     - none (graph-wide)
   * - `known_good_correct.yml <../../.github/workflows/known_good_correct.yml>`_
     - Fails if the generated Bazel fragments drift from ``known_good.json``.
     - **yes**
     - commit step 1.2 output
   * - `bzlmod-lock.yml <../../.github/workflows/bzlmod-lock.yml>`_
     - Verifies ``MODULE.bazel.lock`` is consistent with the module graph.
     - **yes**
     - update lockfile if it fails
   * - `format.yml <../../.github/workflows/format.yml>`_
     - Runs the code-formatting checks.
     - **yes**
     - run the format targets
   * - `codeql-multiple-repo-scan.yml <../../.github/workflows/codeql-multiple-repo-scan.yml>`_
     - Multi-repository CodeQL security scan across the integrated modules.
     - **yes**
     - none
   * - `test_and_docs.yml <../../.github/workflows/test_and_docs.yml>`_
     - Code-quality checks, builds the docs and reports, publishes to Pages.
     - **yes**
     - wire docs in Step 2, reports in Step 7
   * - `check_release_approvals.yml <../../.github/workflows/check_release_approvals.yml>`_
     - Enforces required approvals on PRs targeting ``releases/*`` branches.
     - release branches only
     - none
   * - `build_and_test_linux.yml <../../.github/workflows/build_and_test_linux.yml>`_
     - Builds the Linux x86_64 image and runs feature integration tests on Docker.
     - no
     - none (graph-wide)
   * - `internal_tests.yml <../../.github/workflows/internal_tests.yml>`_
     - Runs the integration tooling tests (``//scripts/tooling:tooling_tests``).
     - no
     - only if you change scripts
   * - `docs_cleanup.yml <../../.github/workflows/docs_cleanup.yml>`_
     - Scheduled cleanup of published documentation versions.
     - no
     - none
   * - `test_integration.yml <../../.github/workflows/test_integration.yml>`_ /
       `reusable_smoke-test.yml <../../.github/workflows/reusable_smoke-test.yml>`_ /
       `reusable_integration-build.yml <../../.github/workflows/reusable_integration-build.yml>`_
     - Smoke-test / reusable build of the latest module ``main`` branches.
     - no
     - add runtime targets to
       `ci/showcase_targets_run.txt <../../ci/showcase_targets_run.txt>`_

.. _reports:

Reports
-------

The consolidated outputs published by the integration. They are built by
``test_and_docs.yml`` and rendered into the documentation site.

.. list-table::
   :header-rows: 1
   :widths: 30 40 30

   * - Report
     - Contents
     - Source / target
   * - Consolidated documentation
     - All integrated module docs merged into one Sphinx site.
     - `BUILD <../../BUILD>`_ ``docs(...)`` → ``bazel run //:docs_combo``
   * - Platform verification report
     - Per-release requirements/architecture verification, safety analyses and
       per-test-case results.
     - `docs/verification_report/platform_verification_report.rst <../../docs/verification_report/platform_verification_report.rst>`_
   * - Unit test summary
     - Per-module unit-test execution table (generated at build time by
       ``quality_runners.py``).
     - `docs/verification_report/unit_test_summary.md <../../docs/verification_report/unit_test_summary.md>`_
   * - Coverage summary
     - Per-module C++ and Rust coverage table (generated at build time by
       ``quality_runners.py``).
     - `docs/verification_report/coverage_summary.md <../../docs/verification_report/coverage_summary.md>`_
   * - C++ coverage (per module)
     - lcov/genhtml line/function/branch report for modules declaring ``cpp``.
     - `scripts/quality_runners.py <../../scripts/quality_runners.py>`_ →
       ``python3 scripts/quality_runners.py --modules-to-test <module>``
   * - Rust coverage reports
     - Per-module Rust line coverage (C0/C1) for modules declaring ``rust``.
     - `rust_coverage/BUILD <../../rust_coverage/BUILD>`_ →
       ``bazel run //rust_coverage:rust_coverage_<module>``
   * - Overall feature & process status
     - Feature/process completion dashboard derived from the pinned module repos.
     - `docs/s_core_v_1/roadmap/overall_status.rst <../../docs/s_core_v_1/roadmap/overall_status.rst>`_
   * - Integration status dashboard
     - Live build/health overview of the integration.
     - `status_dashboard.html <https://eclipse-score.github.io/reference_integration/main/status_dashboard.html>`_
