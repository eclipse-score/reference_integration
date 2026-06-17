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

Step 3 — Get compiled and unit-tested on the default platform
=============================================================

   **What this unlocks:** every module registered in ``known_good.json`` is
   automatically **compiled and run through its unit tests** on the default
   platform (Linux ``x86_64``, ``--config=linux-x86_64``) — no per-module wiring
   is needed. As soon as your module is in the graph (Step 1), its unit tests
   are part of the integration's quality gate.

Unit tests are driven by
`scripts/quality_runners.py <../../scripts/quality_runners.py>`_, which loads
``known_good.json`` and iterates over **every** module under
``modules.target_sw``. For each module it runs ``bazel coverage`` with the
``unit-tests`` config, which builds and tests the module's source tree on the
default Linux ``x86_64`` platform:

.. code-block:: bash

   # what the runner effectively executes per module
   bazel coverage --config=unit-tests \
       --instrumentation_filter=@score_my_module \
       @score_my_module<code_root_path>

   # reproduce locally for a single module
   python3 scripts/quality_runners.py --modules-to-test score_my_module

``--config=unit-tests`` expands to ``--config=linux-x86_64`` (plus
``--build_tests_only`` and a ``-manual`` tag filter), so this is the **default
platform** baseline that every module must pass — independent of the
target-platform images in Step 4.

What you can tune from ``known_good.json``
------------------------------------------

You do not edit ``quality_runners.py`` to control what is tested — the per-module
``metadata`` in ``known_good.json`` (Step 1) drives it:

* ``metadata.code_root_path`` — the target pattern that is built and tested
  (``@score_my_module<code_root_path>``), e.g. ``//src/...``.
* ``metadata.extra_test_config`` — extra ``--flag=value`` build/test settings
  injected for this module (feature flags, config selections).
* ``metadata.exclude_test_targets`` — test targets that must **not** run
  (flaky, environment-specific or not meaningful out-of-tree); they are passed as
  ``-@score_my_module<target>`` exclusions. Supports wildcards such as
  ``//score/json/examples:*``.

So enrolling your module into unit testing requires no extra step beyond Step 1
— you only adjust these fields when the defaults do not fit.

The unit-test results and the code-coverage numbers produced here are exported
into the consolidated reports (markdown summaries on the docs site, HTML
coverage reports and the CI job summary). How and where exactly is described in
Step 7, see :ref:`reporting`.

This runs in the ``test_and_docs`` workflow
(`test_and_docs.yml <../../.github/workflows/test_and_docs.yml>`_), in the same
job as the docs build (see :ref:`ci_checks`).

.. note::

   **Planned refactoring.** As with the documentation build, unit testing is
   currently bundled into the monolithic ``test_and_docs`` workflow together with
   coverage and feature integration tests. This should be split out into a
   **dedicated, reusable unit-test workflow shared across all S-CORE
   repositories**, hosted centrally in the
   `cicd-workflows <https://github.com/eclipse-score/cicd-workflows>`_
   repository, instead of being duplicated per repo.
