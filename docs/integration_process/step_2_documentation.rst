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

Step 2 — Join the documentation and process-compliance checks
=============================================================

.. admonition:: What it unlocks
   :class: tip

   **Docs & process checks** — Your module's documentation appears in the
   single, combined docs site that is built and published for the whole
   integration — and, just as importantly, your module's **requirements,
   architecture and other process artifacts are validated against the S-CORE
   process** as part of the same build. This is usually the first thing you
   *extend the integration with* after the module is in the graph.

Building the docs is not only about rendering pages. The integration uses the
docs-as-code toolchain (`score_docs_as_code
<https://github.com/eclipse-score/docs-as-code>`_, pulled in via
``score_sphinx_bundle`` in `docs/conf.py <https://github.com/eclipse-score/reference_integration/blob/main/docs/conf.py>`_), which runs the
**S-CORE metamodel checks** on every ``needs`` object: requirements,
architecture elements, safety artifacts and their links must conform to the
process model defined in `score_process
<https://github.com/eclipse-score/process_description>`_. If your module's
requirements/architecture are malformed, unlinked or violate the metamodel, the
docs build (and therefore CI) fails — so wiring your module in here is what gets
its process artifacts continuously checked, not just published.

The integration builds one Sphinx site that merges the docs of every integrated
module, and it does so straight from ``known_good.json``: **a module that is in
the integration has its documentation in the site by default**. There is nothing
to add to the top-level ``BUILD`` file.

What happens under the hood: a module that calls docs-as-code's ``docs()`` macro
automatically exposes a public ``//:docs_bundle`` target.
``scripts/known_good/update_module_from_known_good.py`` turns every module in
``known_good.json`` into one mount entry in
`bazel_common/docs_bundles.bzl <https://github.com/eclipse-score/reference_integration/blob/main/bazel_common/docs_bundles.bzl>`_,
which the ``docs(bundles = DOCS_BUNDLES, ...)`` call in the top-level `BUILD
<https://github.com/eclipse-score/reference_integration/blob/main/BUILD>`_ file
consumes. **Which of the two site sections your module lands in follows from the
group it sits in** — no extra declaration, and no toctree to edit: the section
pages (``docs/modules/index.rst`` and ``docs/process_methods_tools/index.rst``)
carry empty toctrees that the mounts fill at build time.

.. list-table::
   :header-rows: 1
   :widths: 26 26 48

   * - Group in ``known_good.json``
     - Mounted under
     - Your module belongs here if it is…
   * - ``modules.target_sw``
     - ``modules/<module_name>``
     - an S-CORE **software module** that ships in the integration
       (communication, persistency, logging, kyron, baselibs, …). This is the
       common case.
   * - ``modules.tooling``
     - ``process_methods_tools/<module_name>``
     - a **tooling / process** repo (platform, process_description,
       docs-as-code, …) rather than a shipped software module.

So for a normal module you do nothing beyond adding it to ``known_good.json``
and re-running the generator:

.. code-block:: bash

   scripts/known_good/update_module_from_known_good.py --known known_good.json \
       --output-dir-modules bazel_common

Commit the regenerated files together with your ``known_good.json`` change —
the :ref:`ci_checks` regenerate them and fail if they drift.

Opting a module out
~~~~~~~~~~~~~~~~~~~

Some modules expose no ``//:docs_bundle``: they do not call ``docs()`` at all,
or their root package cannot be loaded from the integration's dependency graph.
Mounting those would fail the docs build on a missing target, so they opt out
explicitly with ``"docs": false``:

.. code-block:: json

   "score_bazel_platforms": {
       "repo": "https://github.com/eclipse-score/bazel_platforms.git",
       "docs": false,
       "hash": "607672cdf2f05f21af7113dab0849726dd59bf86"
   }

Treat ``"docs": false`` as a gap to close, not a normal state — the point of the
default is that documentation and its process checks are opt-out, not opt-in.

If you need a non-default mount, ``docs`` also accepts an object with
``bundle``, ``mount_at`` and ``attach_to`` keys, which are passed through to the
``docs()`` macro unchanged.

Build the full docs locally to verify your module shows up — or use the
live-preview server which rebuilds on every change:

.. code-block:: bash

   # one-shot full build incl. all modules
   bazel run //:docs

   # live preview in the browser (auto-rebuild)
   bazel run //:live_preview

The docs are built and published by the ``test_and_docs`` workflow (see
:ref:`ci_checks`).

.. note::

   **Planned refactoring.** Today documentation generation is entangled with
   unit tests, coverage and feature integration tests in the single
   ``test_and_docs`` workflow
   (`test_and_docs.yml <https://github.com/eclipse-score/reference_integration/blob/main/.github/workflows/test_and_docs.yml>`_). This
   should be refactored: the documentation build (including the metamodel /
   process-compliance checks) belongs in a **dedicated, reusable workflow shared
   across all S-CORE repositories**, hosted centrally in the
   `cicd-workflows <https://github.com/eclipse-score/cicd-workflows>`_
   repository, instead of being duplicated and maintained per repo.
