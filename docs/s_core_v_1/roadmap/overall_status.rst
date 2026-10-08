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

:hide-toc:

Overall Status
==============

.. important::

   **Data collected on: 2026-10-08**

This page shows how the S-CORE platform grew across releases. Each chart
aggregates one metric over all tracked modules; every bar is split into colour
slots, one slot per contributing module.

The last column, **v0.10 (forecast)**, is not a released state — it is today's
state of the modules pinned in ``known_good.json``, shown as the projection for
the next release.

For the **current** state — per-module and per-component requirements,
architecture, traceability, coverage and work-product status — use the
verification reports, which are generated from the needs data of this
documentation build:

* :doc:`Platform Verification Report </verification_report/platform_verification_report>`
  — feature-level requirements, architecture and inspection statistics.
* :doc:`Module Verification Reports </verification_report/modules/index>`
  — per module: components, component requirements, architectural elements,
  requirements traceability, test coverage and verification work products.

.. note::

   All columns are recounted from the module sources pinned by each release, so
   the series is internally comparable. The counts are source-derived and
   therefore differ from CI figures — test counts are test *definitions*, not
   parameterised CI runs. Treat the numbers as indicative; the verification
   reports are the authoritative source.

.. _overall_status_pa2:

Requirements
------------

.. figure:: /_assets/pa2_impl_progress.svg
   :alt: Requirements per release, split by module
   :width: 880px

   Feature and component requirements across the tracked modules per release.

.. _overall_status_pa3:

Architecture
------------

.. figure:: /_assets/pa3_arch_progress.svg
   :alt: Architecture elements per release, split by module
   :width: 880px

   Feature and component architecture elements across the tracked modules per
   release.

.. _overall_status_pa4:

Implementation
--------------

.. figure:: /_assets/pa4_impl_progress.svg
   :alt: Lines of code per release, split by module
   :width: 880px

   Lines of code across the tracked modules per release, excluding
   documentation and third-party sources.

.. _overall_status_pa5:

Verification
------------

.. figure:: /_assets/pa5_verification_progress.svg
   :alt: Tests per release, split by module
   :width: 880px

   Unit and integration test definitions across the tracked modules per
   release.
