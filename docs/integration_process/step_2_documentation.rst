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
module. To pull yours in:

#. Add your module's ``needs_json`` to the ``docs(...)`` rule's ``data`` list in
   the top-level `BUILD <https://github.com/eclipse-score/reference_integration/blob/main/BUILD>`_ file:

   .. code-block:: python

      docs(
          data = [
              "@score_persistency//:needs_json",
              # ...
              "@score_my_module//:needs_json",
          ],
          known_good = "known_good.json",
          source_dir = "docs",
      )

   This requires your module to expose a ``//:needs_json`` target (i.e. it is a
   docs-as-code module).

#. Add a toctree entry so the module shows up in the navigation. **Which page
   you edit depends on what kind of module it is** — the site groups modules
   into two top-level sections, each backed by its own ``.rst`` page:

   .. list-table::
      :header-rows: 1
      :widths: 22 30 48

      * - Section
        - Page to edit
        - Put your module here if it is…
      * - **Modules**
        - `docs/sw_components.rst <https://github.com/eclipse-score/reference_integration/blob/main/docs/sw_components.rst>`_
        - an S-CORE **software module** that ships in the integration — i.e. it
          lives under ``modules.target_sw`` in ``known_good.json`` (communication,
          persistency, logging, orchestrator, baselibs, …). This is the common
          case.
      * - **Process, Methods & Tools**
        - `docs/process_methods_tools.rst <https://github.com/eclipse-score/reference_integration/blob/main/docs/process_methods_tools.rst>`_
        - a **tooling / process** repo from ``modules.tooling`` (platform, process,
          docs-as-code) rather than a shipped software module.

   For a normal software module, add the entry to the ``Modules`` toctree in
   `docs/sw_components.rst <https://github.com/eclipse-score/reference_integration/blob/main/docs/sw_components.rst>`_, next to the existing
   modules:

   .. code-block:: rst

      Modules
      =======

      .. toctree::
         :titlesonly:
         :maxdepth: 1

         _collections/score_persistency/docs/index
         _collections/score_logging/docs/index
         # ...
         _collections/score_my_module/docs/index

   The ``_collections/score_my_module/docs/index`` path is **not** a file in this
   repository — the docs build mounts every module's documentation under
   ``_collections/<module-repo-name>/`` at build time. So the path must be:

   * ``score_my_module`` — the **module/repository name** as registered in
     ``known_good.json`` (the ``@score_my_module`` repo), and
   * ``docs/index`` — the path of the **documentation root** *inside that
     module's repository* (most modules use ``docs/index``; match whatever your
     module actually exposes via its ``needs_json`` docs target).

Build the full docs locally to verify your module shows up — or use the
live-preview server which rebuilds on every change:

.. code-block:: bash

   # one-shot full build incl. all modules
   bazel run //:docs_combo

   # live preview in the browser (auto-rebuild)
   bazel run //:live_preview_combo_experimental

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
