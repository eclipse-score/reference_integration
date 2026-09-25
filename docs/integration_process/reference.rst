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

The pipelines live under `.github/workflows <https://github.com/eclipse-score/reference_integration/tree/main/.github/workflows>`_. Most
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
   * - `build_and_test_qnx.yml <https://github.com/eclipse-score/reference_integration/blob/main/.github/workflows/build_and_test_qnx.yml>`_
     - Builds the QNX IFS and runs integration tests on QEMU.
     - **yes**
     - none (graph-wide)
   * - `build_and_test_autosd.yml <https://github.com/eclipse-score/reference_integration/blob/main/.github/workflows/build_and_test_autosd.yml>`_
     - Builds the AutoSD OCI image with the Automotive Image Builder.
     - **yes**
     - none (graph-wide)
   * - `build_and_test_ebclfsa.yml <https://github.com/eclipse-score/reference_integration/blob/main/.github/workflows/build_and_test_ebclfsa.yml>`_
     - Builds the EBcLfSA image and runs the high-integrity safety tests.
     - **yes**
     - none (graph-wide)
   * - `known_good_correct.yml <https://github.com/eclipse-score/reference_integration/blob/main/.github/workflows/known_good_correct.yml>`_
     - Fails if the generated Bazel fragments drift from ``known_good.json``.
     - **yes**
     - commit step 1.2 output
   * - `bzlmod-lock.yml <https://github.com/eclipse-score/reference_integration/blob/main/.github/workflows/bzlmod-lock.yml>`_
     - Verifies ``MODULE.bazel.lock`` is consistent with the module graph.
     - **yes**
     - update lockfile if it fails
   * - `format.yml <https://github.com/eclipse-score/reference_integration/blob/main/.github/workflows/format.yml>`_
     - Runs the code-formatting checks.
     - **yes**
     - run the format targets
   * - `codeql-multiple-repo-scan.yml <https://github.com/eclipse-score/reference_integration/blob/main/.github/workflows/codeql-multiple-repo-scan.yml>`_
     - Multi-repository CodeQL security scan across the integrated modules.
     - **yes**
     - none
   * - `test_and_docs.yml <https://github.com/eclipse-score/reference_integration/blob/main/.github/workflows/test_and_docs.yml>`_
     - Code-quality checks, builds the docs and reports, publishes to Pages.
     - **yes**
     - wire docs in Step 2, reports in Step 7
   * - `staged_ci_guard.yml <https://github.com/eclipse-score/reference_integration/blob/main/.github/workflows/staged_ci_guard.yml>`_
     - Fails while the ``staged-ci`` label is set, so a pull request with
       skipped heavy checks cannot be merged (see :ref:`staged_ci`).
     - **yes**
     - none
   * - `check_release_approvals.yml <https://github.com/eclipse-score/reference_integration/blob/main/.github/workflows/check_release_approvals.yml>`_
     - Enforces required approvals on PRs targeting ``releases/*`` branches.
     - release branches only
     - none
   * - `build_and_test_linux.yml <https://github.com/eclipse-score/reference_integration/blob/main/.github/workflows/build_and_test_linux.yml>`_
     - Builds the Linux x86_64 image and runs feature integration tests on Docker.
     - no
     - none (graph-wide)
   * - `internal_tests.yml <https://github.com/eclipse-score/reference_integration/blob/main/.github/workflows/internal_tests.yml>`_
     - Runs the integration tooling tests (``//scripts/tooling:tooling_tests``).
     - no
     - only if you change scripts
   * - `docs_cleanup.yml <https://github.com/eclipse-score/reference_integration/blob/main/.github/workflows/docs_cleanup.yml>`_
     - Scheduled cleanup of published documentation versions.
     - no
     - none
   * - `test_integration.yml <https://github.com/eclipse-score/reference_integration/blob/main/.github/workflows/test_integration.yml>`_ /
       `reusable_smoke-test.yml <https://github.com/eclipse-score/reference_integration/blob/main/.github/workflows/reusable_smoke-test.yml>`_ /
       `reusable_integration-build.yml <https://github.com/eclipse-score/reference_integration/blob/main/.github/workflows/reusable_integration-build.yml>`_
     - Smoke-test / reusable build of the latest module ``main`` branches.
     - no
     - add runtime targets to
       `ci/showcase_targets_run.txt <https://github.com/eclipse-score/reference_integration/blob/main/ci/showcase_targets_run.txt>`_

.. _staged_ci:

Staged CI for integration pull requests
---------------------------------------

A "come together" pull request that bumps every module hash in
``known_good.json`` at once often fails for a reason that is visible long before
the hour-long image builds finish — a module no longer resolves, a target was
renamed, a documentation mount broke. Waiting for the full pipeline on every
push wastes both runner time and the integrator's time.

Adding the ``staged-ci`` label to such a pull request skips the expensive jobs
and leaves only the cheap, ``known_good.json``-derived validation running:

.. list-table::
   :header-rows: 1
   :widths: 46 27 27

   * - Check
     - with ``staged-ci``
     - without the label
   * - ``known_good_correct``, ``bzlmod-lock``, ``format``, ``copyright``
     - runs
     - runs
   * - ``test_and_docs.yml`` — documentation preflight
     - runs
     - runs
   * - ``test_and_docs.yml`` — unit tests, coverage, feature integration tests
     - skipped
     - runs
   * - ``build_and_test_{linux,qnx,autosd,ebclfsa}.yml``
     - skipped
     - runs
   * - ``codeql-multiple-repo-scan.yml``
     - skipped
     - runs
   * - ``staged_ci_guard.yml``
     - **fails** (blocks merge)
     - passes

Workflow
~~~~~~~~

#. Add the ``staged-ci`` label when opening the integration pull request.
#. Iterate until the documentation preflight and the generator checks are green.
#. Remove the label. The full pipeline runs, and ``Staged CI Guard`` turns green.
#. Merge once everything passes.

The label only takes effect on the next workflow run, which is why every gated
workflow listens for the ``labeled`` and ``unlabeled`` pull-request events.

.. note::

   ``Staged CI Guard`` must be configured as a **required** status check in the
   repository's branch-protection settings. GitHub reports a job skipped via an
   ``if:`` condition as *skipped* and treats a skipped required check as
   satisfied — without the guard, a staged pull request would be mergeable even
   though none of the heavy checks ever ran.

   Staging is a manual override for a supervised integration pull request, not a
   way to merge unvalidated changes. The full pipeline still has to pass before
   the merge.

.. _disabling_a_module:

Temporarily disabling a module
------------------------------

Staging CI buys time to look at a failure; it does not remove the failure. When
a single module blocks the whole integration — an upstream change that will not
land before the next cycle, a broken dependency, a test that cannot pass yet —
that module can be taken out of the integration without losing its pinned state.

Add ``"enabled": false`` together with a mandatory ``"disabled_reason"`` to its
entry in ``known_good.json``:

.. code-block:: json

   "score_example": {
     "repo": "https://github.com/eclipse-score/example.git",
     "hash": "0123456789abcdef0123456789abcdef01234567",
     "enabled": false,
     "disabled_reason": "blocked by eclipse-score/example#123, re-enable after it lands",
     "metadata": { }
   }

The hash, the ``bazel_patches`` list and the metadata stay in the file, so
re-enabling the module is a two-line revert rather than a reconstruction from
the git history. Deleting the entry instead would discard exactly the state the
next integrator needs.

After the edit, regenerate the Bazel fragments as usual (Step 1) and commit them
together with the ``known_good.json`` change:

.. code-block:: bash

   python3 scripts/known_good/update_module_from_known_good.py

A disabled module then contributes no ``bazel_dep``/``git_override`` entry, no
coverage target, no documentation mount, no unit-test run and no SBOM entry.
The generator prints every disabled module and its reason on each run, so the
state cannot decay into an unnoticed permanent one.

What the flag does not do
~~~~~~~~~~~~~~~~~~~~~~~~~

The flag governs the **generated** artefacts only. Anything that names the
module by hand keeps naming a module that no longer exists, and Bazel reports
that far away from ``known_good.json``. Two such references are checked
explicitly and abort the regeneration with the offending lines:

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Reference
     - Why it must go with the module
   * - ``--@module//...`` flags in ``.bazelrc``
     - Bazel resolves them on *every* invocation, including ``bazel query``, so
       the whole workspace becomes unusable.
   * - ``extra_test_config`` / ``exclude_test_targets`` of another module, and
       ``sbom.tracked_modules``
     - The entry would point into a module the build no longer contains.

Other references are **not** detected automatically and have to be removed by
hand — hand-written ``BUILD`` files such as ``images/*/BUILD``,
``showcases/standalone/BUILD`` and the feature-integration test scenarios, plus
any test in ``feature_integration_tests/itf/`` that exercises the module. In
practice the flag is therefore sufficient for a module that only contributes
documentation, coverage and unit tests, and is only the first step for a module
that is wired into the images, the showcases or the integration tests.

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
     - `BUILD <https://github.com/eclipse-score/reference_integration/blob/main/BUILD>`_ ``docs(...)`` → ``bazel run //:docs``
   * - Platform verification report
     - Per-release requirements/architecture verification, safety analyses and
       per-test-case results.
     - `docs/verification_report/platform_verification_report.rst <https://github.com/eclipse-score/reference_integration/blob/main/docs/verification_report/platform_verification_report.rst>`_
   * - Unit test summary
     - Per-module unit-test execution table (generated at build time by
       ``quality_runners.py``).
     - `docs/verification_report/unit_test_summary.md <https://github.com/eclipse-score/reference_integration/blob/main/docs/verification_report/unit_test_summary.md>`_
   * - Coverage summary
     - Per-module C++ and Rust coverage table (generated at build time by
       ``quality_runners.py``).
     - `docs/verification_report/coverage_summary.md <https://github.com/eclipse-score/reference_integration/blob/main/docs/verification_report/coverage_summary.md>`_
   * - C++ coverage (per module)
     - lcov/genhtml line/function/branch report for modules declaring ``cpp``.
     - `scripts/quality_runners.py <https://github.com/eclipse-score/reference_integration/blob/main/scripts/quality_runners.py>`_ →
       ``python3 scripts/quality_runners.py --modules-to-test <module>``
   * - Rust coverage reports
     - Per-module Rust line coverage (C0/C1) for modules declaring ``rust``.
     - `rust_coverage/BUILD <https://github.com/eclipse-score/reference_integration/blob/main/rust_coverage/BUILD>`_ →
       ``bazel run //rust_coverage:rust_coverage_<module>``
   * - Overall feature & process status
     - Feature/process completion dashboard derived from the pinned module repos.
     - `docs/s_core_v_1/roadmap/overall_status.rst <https://github.com/eclipse-score/reference_integration/blob/main/docs/s_core_v_1/roadmap/overall_status.rst>`_
   * - Integration status dashboard
     - Live build/health overview of the integration.
     - `status_dashboard.html <../status_dashboard.html>`_
