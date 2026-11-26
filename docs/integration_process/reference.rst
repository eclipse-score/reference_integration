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
   * - `check_release_approvals.yml <https://github.com/eclipse-score/reference_integration/blob/main/.github/workflows/check_release_approvals.yml>`_
     - Enforces required approvals on PRs targeting ``releases/*`` branches.
     - release branches only
     - none
   * - `build_and_test_linux.yml <https://github.com/eclipse-score/reference_integration/blob/main/.github/workflows/build_and_test_linux.yml>`_
     - Builds the Linux x86_64 image and runs feature integration tests on Docker.
     - no
     - none (graph-wide)
   * - `build_and_test_linux_target.yml <https://github.com/eclipse-score/reference_integration/blob/main/.github/workflows/build_and_test_linux_target.yml>`_
     - Builds the Linux x86_64 and aarch64 release archives, runs the showcases from them on
       stock Ubuntu and Debian containers and attaches them to releases.
     - no
     - none (graph-wide)
   * - `internal_tests.yml <https://github.com/eclipse-score/reference_integration/blob/main/.github/workflows/internal_tests.yml>`_
     - Runs the integration tooling tests (``//:internal_tests``).
     - no
     - only if you change scripts
   * - `docs_cleanup.yml <https://github.com/eclipse-score/reference_integration/blob/main/.github/workflows/docs_cleanup.yml>`_
     - Scheduled cleanup of published documentation versions.
     - no
     - none
   * - `on_repo_change.yml <https://github.com/eclipse-score/reference_integration/blob/main/.github/workflows/on_repo_change.yml>`_ /
       `unified_workflow.yml <https://github.com/eclipse-score/reference_integration/blob/main/.github/workflows/unified_workflow.yml>`_
     - Unified pipeline for pull requests, the merge queue, ``main`` and releases (check
       ``CI / CI status``). Runs alongside the workflows above until it becomes the required check.
     - not yet
     - none
   * - `on_schedule.yml <https://github.com/eclipse-score/reference_integration/blob/main/.github/workflows/on_schedule.yml>`_
     - Manual run of the unified pipeline, by default against the latest module ``main`` branches.
       The nightly schedule is currently deactivated.
     - no
     - none

.. _unified_ci_pipeline:

Unified CI pipeline
~~~~~~~~~~~~~~~~~~~

All CI runs through one reusable pipeline, ``.github/workflows/unified_workflow.yml``.
It has no event triggers of its own (``workflow_call`` only) and is called by two
thin callers:

.. list-table::
   :header-rows: 1
   :widths: 14 26 14 14 32

   * - Caller
     - Event
     - Test level
     - known_good
     - Publishing
   * - ``on_repo_change.yml``
     - ``pull_request`` (same repo and forks)
     - ``pr``
     - pinned
     - documentation preview under ``pr-<number>/`` (same-repository pull requests;
       fork pull requests download the ``github-pages-<sha>`` artifact of the run)
   * - ``on_repo_change.yml``
     - ``merge_group``
     - ``merge``
     - pinned
     - none
   * - ``on_repo_change.yml``
     - ``push`` to ``main``
     - ``full``
     - pinned
     - documentation (GitHub Pages)
   * - ``on_repo_change.yml``
     - ``release`` created
     - ``full_clean``
     - pinned
     - documentation and release assets
   * - ``on_schedule.yml``
     - ``schedule`` (02:30 UTC, currently deactivated)
     - ``full``
     - latest
     - none
   * - ``on_schedule.yml``
     - ``workflow_dispatch``
     - choice, default ``full``
     - choice, default latest
     - none

Test levels
^^^^^^^^^^^

The levels are cumulative: ``pr`` < ``merge`` < ``full`` < ``full_clean``.

- **pr**: fast checks (common checks for format, copyright and the Bzlmod lockfile,
  internal tooling tests, known_good consistency), module unit/coverage tests, Linux FIT/ITF/PIT and
  module integration tests, Linux image and SBOM, Linux release archives on stock
  distributions, EB corbos Linux and AutoSD, documentation build.
- **merge**: ``pr`` on the merge-queue candidate, where QNX is mandatory. Test results
  may come from the Bazel cache.
- **full**: reserved for future expansion. Today it runs exactly what ``merge`` runs.
- **full_clean**: ``full`` built and tested from scratch. Disk caches are neither
  restored nor saved in any job. Every ``bazel test`` call additionally gets
  ``--nocache_test_results`` on its command line (the Linux, QNX and integration-test
  jobs, ``scripts/module_tests.py run --nocache-test-results`` and
  ``scripts/quality_runners.py`` without ``--trust-cache``). The AutoSD, EB corbos Linux
  and Linux release-archive jobs only build with Bazel and test outside of it, so for
  them the disabled disk cache is what makes the run clean. The QNX job, which may run
  on a persistent self-hosted runner, also runs ``bazel clean --expunge`` first, so no
  output base or local action cache survives from an earlier run. ``~/.bazelrc`` is
  never modified for this, because it persists on self-hosted runners.

The QNX x86_64 image, ITF and PIT run whenever the QNX secrets
(``SCORE_QNX_LICENSE``, ``SCORE_QNX_USER``, ``SCORE_QNX_PASSWORD``,
``SCORE_BOT_QNX_PKG_PAT``) are available to the run. Pull requests from branches of
this repository therefore build QNX; fork and Dependabot pull requests, which GitHub
gives no secrets, skip it. From the ``merge`` level up, missing secrets fail the run
in ``eclipse-score/reference_integration`` instead of silently dropping QNX.

For ``pull_request``, ``merge_group``, ``push`` and ``release`` the ``prepare`` job
derives the level from the event and ignores all workflow inputs. Inputs are honored
for ``schedule`` and ``workflow_dispatch`` only. This guards against inputs, not
against edits: for ``pull_request`` and ``merge_group`` the pipeline itself comes from
the candidate commit, so a change can modify it like any other file. That grants
nothing extra, because fork pull requests run with a read-only token and without
secrets, and branch authors already have write access.

Pipeline stages
^^^^^^^^^^^^^^^

.. mermaid::

   flowchart TB
       Trigger(["Pull request · Merge queue · Push to main · Release · Nightly · Manual"])
       Trigger --> Prepare["prepare<br/>Derive test level, known_good mode,<br/>QNX, publishing and required jobs"]

       subgraph Fast["Fast checks (parallel)"]
           direction LR
           Common["Common checks<br/>(format, copyright,<br/>Bzlmod lockfile)"]
           Internal["Internal tooling tests"]
           KnownGood["known_good consistency"]
       end

       Prepare --> Fast
       Fast --> Gate["gate<br/>All fast checks passed"]
       Gate --> Resolve["resolve<br/>Resolve the module graph once<br/>(pinned · latest · override)"]

       subgraph Intensive["Builds and tests (parallel)"]
           direction LR
           Modules["Module tests"]
           Linux["Linux image,<br/>ITF and SBOM"]
           Integration["Linux FIT, PIT and<br/>module integration tests"]
           Target["Linux release<br/>archives"]
           Ebclfsa["EB corbos Linux"]
           AutoSD["AutoSD"]
           Qnx["QNX<br/>(if secrets available)"]
       end

       Resolve --> Intensive
       Intensive --> Docs["docs<br/>Build documentation from<br/>test reports and coverage"]
       Docs --> Publish["docs-deploy · release-publish<br/>(only when permitted)"]
       Publish --> Status["CI status<br/>Compare all job results<br/>with the required set"]

#. ``prepare`` (``scripts/prepare_pipeline.py``) derives the level, the known_good
   mode, whether QNX runs, whether to publish and the list of required jobs. Every
   job builds ``github.sha``: the PR merge commit, the merge-queue head or the pushed
   commit.
#. Fast checks run in parallel on the committed candidate. The ``gate`` job requires
   all of them. The common checks and the internal tooling tests call the shared
   ``on-pr.yml`` and ``bazel.yml`` workflows of
   `eclipse-score/cicd-workflows <https://github.com/eclipse-score/cicd-workflows>`_;
   the common checks run formatting, copyright and the Bzlmod lockfile checks one
   after another in a single job.
#. ``resolve`` resolves the module graph once: ``pinned`` uses the committed files,
   ``latest`` the module ``main`` branches (``scripts/known_good/update_module_latest.py``),
   ``override`` one module (``scripts/known_good/override_known_good_repo.py``). It
   regenerates the Bazel fragments and the lockfile and uploads them as the
   ``resolved-inputs`` artifact. Every later job restores it before setting up Bazel
   and builds with ``--lockfile_mode=error``.
#. The execution leaves (``build_and_test_*.yml``, ``module_tests.yml``) and the Linux
   FIT/PIT/module-integration-test job run in parallel, QNX only when its secrets are
   available (see above).
#. ``docs`` builds the documentation from the uploaded test reports.
#. ``docs-deploy`` and ``release-publish`` run only in
   ``eclipse-score/reference_integration`` and only from artifacts of the same run.
   ``docs-deploy`` publishes ``main/`` for ``push`` to ``main``, the tag folder for a
   ``release`` and a ``pr-<number>/`` preview for pull requests from branches of this
   repository. Fork pull requests get no deployed preview, because their token is
   read-only. Their documentation is still built: download the ``github-pages-<sha>``
   artifact (``github-pages.tar``) from the workflow run's summary page.
   ``release-publish`` runs for ``release`` only and checks the downloaded assets
   against an explicit list (Linux, EB corbos Linux and AutoSD packages, the AutoSD
   images, the test-report ZIP and the build tools SBOM): a missing or unexpected asset
   fails the job. Both are switched off as long as
   ``PUBLISHING_ENABLED`` in ``unified_workflow.yml`` is ``'false'`` (see
   `Migration status`_).
#. ``CI status`` (check name ``CI / CI status``) compares every job result with the
   required set. A required job that failed, was cancelled or was skipped fails the
   run. Intentional skips (QNX without secrets, publishers) are listed but do not
   fail it.

Artifacts
^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 34 33 33

   * - Artifact
     - Producer
     - Consumers
   * - ``resolved-inputs``
     - ``resolve``
     - every Bazel job
   * - ``module-tests-<module>``
     - ``module_tests.yml``
     - ``docs``, release ZIP
   * - ``test-reports-<suite>-<platform>``
     - Linux, QNX and integration-test jobs
     - ``docs``, release ZIP
   * - ``test-reports-zip``
     - ``docs``
     - ``release-publish``
   * - ``build-tools-sbom-<sha>``, ``score-release-*``, AutoSD images
     - build jobs
     - ``release-publish``
   * - ``github-pages-<sha>``
     - ``docs``
     - ``docs-deploy``

Test report artifacts keep the ``bazel-testlogs/``-relative layout
(``external/<repo>+/.../test.xml``), because the documentation's source code linker
and the release ZIP depend on it. Linux reports are the documentation evidence; QNX
reports are kept in a separate artifact.

Caller contract
^^^^^^^^^^^^^^^

``unified_workflow.yml`` accepts the inputs ``test_level``, ``known_good_mode`` and
``module_override`` (``<module>@<sha>`` or ``<module>@<repo_url>@<sha>``);
``on_repo_change.yml`` passes no inputs. It declares no secrets, because both callers
use ``secrets: inherit``. It uses ``SCORE_QNX_LICENSE``, ``SCORE_QNX_USER``,
``SCORE_QNX_PASSWORD``, ``SCORE_BOT_QNX_PKG_PAT`` and ``UBUNTU_SNAPSHOT_MIRROR_URL``
when they are available. Callers grant
the maximum permissions (``contents: write``, ``pages: write``, ``id-token: write``,
``pull-requests: write``). Every job in the pipeline declares its own minimum, and jobs
that run candidate code get ``contents: read``. Concurrency of a pipeline run is
defined in the callers. The ``build_and_test_*.yml`` leaves keep a concurrency group
for their standalone runs; when called, their group is unique per run. ``docs-deploy``
shares the ``docs-publish`` group with the daily maintenance workflow (``daily.yml``),
which cleans up old documentation versions: both push to ``gh-pages``, so they run one
at a time, and waiting deploys are queued instead of cancelled.

Forks and the merge queue
^^^^^^^^^^^^^^^^^^^^^^^^^

- Fork pull requests run at the ``pr`` level with a read-only token and no secrets.
  They skip QNX, and module tests use the public Ubuntu snapshots instead of the
  ``UBUNTU_SNAPSHOT_MIRROR_URL`` mirror.
- The unified pipeline never runs under ``pull_request_target``, so it never runs fork
  code with secrets. Pull requests from branches of this repository get the secrets, as
  their authors already have write access. For fork pull requests, the merge queue
  is the first run with QNX, after review.
- The previous workflows ``build_and_test_qnx.yml`` and ``test_and_docs.yml`` still
  have their own ``pull_request_target`` trigger for standalone runs. It is removed
  together with their other event triggers once the unified pipeline is the required
  check (see `Migration status`_).
- Forks of this repository never publish, and GitHub disables scheduled workflows in
  forks.

Migration status
^^^^^^^^^^^^^^^^

The unified pipeline currently runs alongside the previous per-topic workflows as a
non-required check and publishes nothing (``PUBLISHING_ENABLED: 'false'``), so the
previous workflows remain the only ones that deploy documentation and upload release
assets. Once it is required, the event triggers of the
``build_and_test_*.yml``, ``test_and_docs.yml``, ``format.yml``, ``copyright.yml``,
``internal_tests.yml``, ``known_good_correct.yml`` and ``bzlmod-lock.yml`` workflows
will be removed and ``PUBLISHING_ENABLED`` set to ``'true'`` in the same change.
``reusable_smoke-test.yml``, ``reusable_integration-build.yml`` and
``test_integration.yml`` have been removed.

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
   * - Release-wide progress overview
     - Per-release progress charts, current release split by module.
     - `docs/s_core_v_1/releases/progress_overview.rst <https://github.com/eclipse-score/reference_integration/blob/main/docs/s_core_v_1/releases/progress_overview.rst>`_
   * - Integration status dashboard
     - Live build/health overview of the integration.
     - `status_dashboard.html <../status_dashboard.html>`_
