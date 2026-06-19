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

Step 1 — Adding module to reference integration
=================================================

.. admonition:: What it unlocks
   :class: tip

   **Module in the graph** — Your module becomes a *known* part of the
   integration, pinned at an exact commit, enters the **Bazel module graph** and
   builds cleanly against every other module. This is the foundation every later
   step builds on — afterwards ``@score_my_module//...`` resolves and any other
   target can depend on your module.

1.1 Register the module in ``known_good.json``
----------------------------------------------

``known_good.json`` is the single source of truth for which modules — and at
which commit — are part of the integration. Every other generated file is
derived from it, so this is always the first change.

Open `known_good.json <https://github.com/eclipse-score/reference_integration/blob/main/known_good.json>`_. It has two top-level groups
under ``modules``:

* ``target_sw`` — the S-CORE software modules that are built and shipped
  (baselibs, communication, persistency, logging, …). **Your module goes here.**
* ``tooling`` — supporting tooling repos (docs-as-code, process, platform, …).

Add an entry for your module under ``modules.target_sw``:

.. code-block:: json

   "score_my_module": {
       "repo": "https://github.com/eclipse-score/my_module.git",
       "hash": "0000000000000000000000000000000000000000",
       "metadata": {
           "code_root_path": "//src/...",
           "langs": ["rust"],
           "extra_test_config": [],
           "exclude_test_targets": [],
           "rust_coverage_config": "ferrocene-coverage"
       }
   }

Field reference
~~~~~~~~~~~~~~~

``repo`` (required)
   HTTPS clone URL of the module repository.

``hash`` (required, mutually exclusive with ``version``)
   Exact commit to pin. Use ``version`` instead if the module is published to a
   Bazel registry (this emits a ``single_version_override`` rather than a
   ``git_override``).

``bazel_patches`` (optional)
   List of patch labels applied on top of the checked-out commit (see
   :ref:`patches`).

``metadata.code_root_path`` (default ``//score/...``)
   Bazel target pattern that points at the module's source root. Used to scope
   test discovery and Rust coverage queries (e.g. ``//src/...``).

``metadata.langs`` (default ``["cpp", "rust"]``)
   Languages used by the module. ``rust`` enables a generated Rust coverage
   report (see :ref:`reporting`).

``metadata.extra_test_config``
   Extra ``--//flag=value`` build settings injected when building/testing this
   module (feature flags, config selections, …).

``metadata.exclude_test_targets``
   Test targets that must **not** run in the integration (flaky, environment
   specific, or not meaningful out-of-tree). Supports wildcards such as
   ``//score/json/examples:*``.

``metadata.rust_coverage_config`` (default ``ferrocene-coverage``)
   The Bazel coverage config to use for the generated Rust coverage report.

``pin_version`` (optional, default ``false``)
   When ``true``, the automatic "update to latest HEAD" scripts will leave this
   module's hash untouched.

.. note::

   To bump an existing entry to the latest commit on a branch you can use
   ``scripts/known_good/update_module_latest.py`` instead of editing the hash by
   hand. The first integration, however, is added manually.


1.2 Regenerate the Bazel module fragments
-----------------------------------------

   Your module now enters the **Bazel module graph**. From now on
   ``@score_my_module//...`` resolves and any other target — showcases, docs,
   other modules — can depend on it. (If it declares ``rust``, its Rust coverage
   target is generated here too.)

The Bazel files are **generated** from ``known_good.json`` — never edit them by
hand. After editing the JSON, regenerate them:

.. code-block:: bash

   python3 scripts/known_good/update_module_from_known_good.py

This (re)writes:

* `bazel_common/score_modules_target_sw.MODULE.bazel <https://github.com/eclipse-score/reference_integration/blob/main/bazel_common/score_modules_target_sw.MODULE.bazel>`_
  — a ``bazel_dep`` + ``git_override`` block for your module. This file is
  pulled into the build via ``include(...)`` in
  `MODULE.bazel <https://github.com/eclipse-score/reference_integration/blob/main/MODULE.bazel>`_.
* `rust_coverage/BUILD <https://github.com/eclipse-score/reference_integration/blob/main/rust_coverage/BUILD>`_ — a
  ``rust_coverage_report`` target for every module that declares ``rust`` in its
  ``langs`` (skipped for C++-only modules).

Next, refresh the Bazel lockfile so it reflects the updated module graph:

.. code-block:: bash

   bazel mod deps --lockfile_mode=update

Adding your module introduces a new ``bazel_dep`` / ``git_override`` into the
module graph, which changes the set of resolved dependencies. Running ``bazel
mod deps`` with ``--lockfile_mode=update`` re-resolves the graph and writes the
new dependencies into `MODULE.bazel.lock <https://github.com/eclipse-score/reference_integration/blob/main/MODULE.bazel.lock>`_. Committing
an up-to-date lockfile keeps the dependency resolution reproducible for everyone
and is required by the ``Bzlmod Lockfile Check`` CI job (see section 1.4), which
fails if the committed lockfile is out of sync with the module graph.

Commit the regenerated files together with the ``known_good.json`` change. CI
verifies that the generated files are in sync with the JSON (see the
``known_good_correct`` workflow), so a manual edit that drifts from the JSON
will fail.

.. _patches:

1.3 (optional) Add Bazel patches
--------------------------------

If the module does not build cleanly out-of-tree (e.g. label visibility issues),
add patch files under ``patches/<module>/`` and reference them from the
``bazel_patches`` list of the module entry in ``known_good.json``. See
`patches/communication <https://github.com/eclipse-score/reference_integration/tree/main/patches/communication>`_ for a worked example. The
generator emits ``patches = [...]`` with ``patch_strip = 1`` automatically.

.. note::

   Patching a module should be the **exception, not the rule**. A patch keeps a
   local divergence from the upstream module that has to be maintained and
   re-based on every update. Prefer fixing the underlying issue in the module's
   own repository so it builds cleanly out-of-tree, and only reach for a patch
   as a temporary, last-resort workaround.

1.4 CI checks that the module was added correctly
-------------------------------------------------

Once the changes above are pushed, two **gating** CI jobs verify that the module
was wired in consistently. They do not build your module's code — they only
check that the generated metadata is in sync with ``known_good.json``:

.. list-table::
   :header-rows: 1
   :widths: 28 48 24

   * - Check (workflow)
     - What it verifies
     - Fix if it fails
   * - Known Good Matches Bazel
       (`known_good_correct.yml <https://github.com/eclipse-score/reference_integration/blob/main/.github/workflows/known_good_correct.yml>`_)
     - Re-runs ``update_module_from_known_good.py`` and fails if the generated
       Bazel fragments differ from what you committed — i.e. ``known_good.json``
       and the generated ``*.MODULE.bazel`` / ``rust_coverage/BUILD`` are out of
       sync.
     - re-run step 1.2 and commit the regenerated files
   * - Bzlmod Lockfile Check
       (`bzlmod-lock.yml <https://github.com/eclipse-score/reference_integration/blob/main/.github/workflows/bzlmod-lock.yml>`_)
     - Verifies ``MODULE.bazel.lock`` is consistent with the updated module
       graph (your new ``bazel_dep`` / ``git_override``).
     - refresh and commit ``MODULE.bazel.lock``

Both jobs run in the merge queue, so they must be green before the pull request
can be merged. The full catalogue of checks is under :ref:`ci_checks`.
