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

Module Verification Reports
============================

This page lists the per-module verification reports.

Reports built into this site
----------------------------

These reports are generated from the respective module's own needs data using
the module verification report template introduced by docs-as-code.

* :doc:`Baselibs </modules/score_baselibs/verification_report/module_verification_report>`
* :doc:`Lifecycle </modules/score_lifecycle/verification_report/index>`
* :doc:`Logging </modules/score_logging/verification_report/module_verification_report>`
* :doc:`Persistency <persistency/persistency_verification_report>`

.. toctree::
   :titlesonly:
   :hidden:

   Baselibs </modules/score_baselibs/verification_report/module_verification_report>
   Lifecycle </modules/score_lifecycle/verification_report/index>
   Logging </modules/score_logging/verification_report/module_verification_report>
   Persistency <persistency/persistency_verification_report>

Reports generated outside docs-as-code
--------------------------------------

Communication does not describe its safety case with docs-as-code. It uses the
``dependable_element`` rule from `eclipse-score/tooling
<https://github.com/eclipse-score/tooling>`__, which generates a self-contained
multi-page report per dependable element — architecture, components, units,
assumed system and a *L.O.B.S.T.E.R.* traceability report over feature
requirements, failure modes, control measures and root causes.

Those pages are produced by Communication's own documentation job and published
to its GitHub Pages site, so they are linked here rather than mounted.

.. list-table::
   :header-rows: 1
   :widths: 25 37 38

   * - Dependable element
     - Report
     - Traceability
   * - ``mw_com`` (LoLa)
     - `Dependable element: mw_com <https://eclipse-score.github.io/communication/latest/docs/sphinx/mw_com_index/index.html>`__
     - `L.O.B.S.T.E.R. report (mw_com) <https://eclipse-score.github.io/communication/latest/docs/sphinx/mw_com_index/traceability_report/index.html>`__
   * - ``message_passing``
     - `Dependable element: message_passing <https://eclipse-score.github.io/communication/latest/docs/sphinx/dependable_element_message_passing_index/index.html>`__
     - `L.O.B.S.T.E.R. report (message_passing) <https://eclipse-score.github.io/communication/latest/docs/sphinx/dependable_element_message_passing_index/traceability_report/index.html>`__

.. note::

   The links above point at Communication's ``latest`` documentation, which
   tracks its ``main`` branch. They are therefore **not** pinned to the
   Communication revision recorded in ``known_good.json``.

.. note::

   Mounting these reports into this site is currently not possible. The
   generated documentation targets are ``testonly``, and a non-testonly target
   such as this site's documentation cannot depend on them.

   ``dependable_element`` only *defaults* to ``testonly = True``, but passing
   ``testonly = False`` does not help: the ``deps`` of a dependable element
   reference the ``<name>`` target of other dependable elements, and that
   target is declared as a Bazel ``test`` rule — which is unconditionally
   ``testonly``. For ``message_passing`` the point is moot anyway, since it
   declares real test dependencies. Resolving this therefore requires a change
   in ``eclipse-score/tooling``.
