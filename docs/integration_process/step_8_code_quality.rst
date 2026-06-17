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

Step 8 — Code quality
=====================

   **What this unlocks:** your module's source is **statically analysed and
   style-checked** on every pull request, on top of the unit, component and
   integration tests of the previous steps.

The integration runs several language-specific code-quality checks. They operate
on ``//...`` (or on the pinned module checkouts), so they pick up your module
automatically once it is in the graph — there is nothing module-specific to wire
in.

What runs today
---------------

* **Formatting checks** (all languages) —
  `format.yml <../../.github/workflows/format.yml>`_ runs the shared S-CORE
  formatter (a reusable workflow from
  `cicd-workflows <https://github.com/eclipse-score/cicd-workflows>`_) and fails
  if any file is not formatted. Reproduce / fix locally by running the format
  targets before pushing.
* **Bazel Clippy** (Rust) — Rust static analysis runs through the ``rules_rust``
  Clippy aspect over the Rust targets, flagging lint violations as build errors.
* **CodeQL multi-repo scan** (C++) —
  `codeql-multiple-repo-scan.yml <../../.github/workflows/codeql-multiple-repo-scan.yml>`_
  checks out every module pinned in ``known_good.json`` and runs CodeQL with the
  **MISRA C++ coding standards** pack across all of them.

.. note::

   **Missing — to be introduced.** There is no **clang-tidy** stage for C++ yet.
   clang-tidy is planned to complement the CodeQL / MISRA scan for C++ static
   analysis, but it is currently not wired into the integration or its CI. Until
   then, C++ static analysis relies on the CodeQL scan only.

Generated reports
-----------------

The CodeQL scan exports its findings as build artifacts on the workflow run:

* a **SARIF** result file (``sarif-results/cpp.sarif``), uploaded as the
  ``codeql-sarif-results`` artifact, and
* a human-readable **HTML report** (``codeql-report.html``), generated from the
  SARIF with ``sarif-tools`` and uploaded as the ``codeql-html-report``
  artifact.

Download these from the *Artifacts* section of the CodeQL workflow run to review
the C++ findings. The formatting and Clippy checks do not produce a separate
report — they pass or fail directly on the workflow run, with the offending
files / lints shown in the job log.
