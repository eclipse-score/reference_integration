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

S-CORE Platform v0.10 release note
====================================

.. document:: S-CORE v0.10 release note
   :id: doc__score_v010_release_note
   :status: draft
   :safety: QM
   :security: YES
   :realizes: wp__platform_sw_release_note
   :version: 1

| **Platform Name:** S-CORE
| **Release Tag:** v0.10.0
| **Origin Release Tag:** v0.9.0
| **Release Date:** 2026-11-02


📋 Overview
^^^^^^^^^^^^

This document provides an overview of the changes, improvements, and bug fixes
included in the software platform release version v0.10.0 as compared to the
previous platform release (v0.9.0).


📜 Disclaimer
--------------

This release note does not "release for production", as it does not come with a
safety argumentation and a performed safety assessment.
The work products compiled in the safety package are created with care according
to a process satisfying standards, but the project, being a non-profit and open
source organization, can not take over any liability for its content.


🔄 Changes to the Platform
^^^^^^^^^^^^^^^^^^^^^^^^^^^

✨ New Features
----------------

Module Tests in the Module Workspace (DR-008)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each integrated software module now runs its own unit tests and coverage in its
own Bazel workspace, against the dependency versions resolved by the reference
integration, with one CI job per module. The test arguments of each module are
kept in ``known_good.json`` (``metadata.test_args``), the shared build settings
in ``bazel_common/unified.bazelrc``. Locally:
``python3 scripts/module_tests.py run <module>``
(`PR #398 <https://github.com/eclipse-score/reference_integration/pull/398>`__).

Shared Image Packaging
~~~~~~~~~~~~~~~~~~~~~~

The QNX images are built with ``score_rules_imagefs`` 0.1.0. Application files
and configuration that both QNX images and the Linux image use are defined once
in ``//images/common/apps``, ``//images/qnx_common/build`` and
``//images/qnx_common/configs``
(`PR #349 <https://github.com/eclipse-score/reference_integration/pull/349>`__,
`PR #389 <https://github.com/eclipse-score/reference_integration/pull/389>`__).

SBOM Generation
~~~~~~~~~~~~~~~

Added generation of a Software Bill of Materials for the product dependencies
(SPDX and CycloneDX) and for the build tools (SPDX), see the "Software Bill of
Materials" section of the README
(`PR #304 <https://github.com/eclipse-score/reference_integration/pull/304>`__).

Module Integration Tests
~~~~~~~~~~~~~~~~~~~~~~~~

The integration tests of Lifecycle, Logging and Persistency run in the reference
integration, and their results are linked to the requirements in the
verification reports
(`PR #385 <https://github.com/eclipse-score/reference_integration/pull/385>`__,
`PR #387 <https://github.com/eclipse-score/reference_integration/pull/387>`__).
The new infrastructure module Tools provides the pytest setup of the Persistency
tests (`PR #388 <https://github.com/eclipse-score/reference_integration/pull/388>`__).

Documentation and Verification Reports
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- The documentation of the Time module is part of the integrated documentation
  (`PR #348 <https://github.com/eclipse-score/reference_integration/pull/348>`__).
- The module verification reports of Logging and Lifecycle are linked from the
  verification report overview
  (`PR #367 <https://github.com/eclipse-score/reference_integration/pull/367>`__,
  `PR #373 <https://github.com/eclipse-score/reference_integration/pull/373>`__).
- The Unit Tests and Coverage summaries are nested under the Platform
  Verification Report
  (`PR #358 <https://github.com/eclipse-score/reference_integration/pull/358>`__).

💥 Breaking Changes
--------------------

Reference Integration: Resolved-Dependency Override Removed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The resolved-dependency override introduced in v0.9
(``scripts/known_good/resolved_dependencies.py`` and
``scripts/known_good/module_patches.py``) and the generated
``rust_coverage/BUILD`` were removed; module tests no longer run inside the
reference integration workspace
(`PR #398 <https://github.com/eclipse-score/reference_integration/pull/398>`__).
Action required: run module tests with ``scripts/module_tests.py`` and keep
their test arguments in ``known_good.json`` (``metadata.test_args``).

Baselibs
~~~~~~~~

Baselibs is integrated at a commit after ``v0.2.14`` and contains breaking
changes of ``v0.2.13`` and ``v0.2.14`` (see the `Baselibs release notes
<https://github.com/eclipse-score/baselibs/releases>`__):

- ``score/datetime_converter`` was removed
  (`PR #471 <https://github.com/eclipse-score/baselibs/pull/471>`__). Use POSIX
  or C library time APIs instead.
- The unused ``score/os`` libraries ``cpuid``, ``file_stream`` and ``make_dev``
  were removed (`PR #535 <https://github.com/eclipse-score/baselibs/pull/535>`__).
- The deprecated ``//src`` Bazel aliases and the string and atomic shims in
  ``//score/memory`` were removed
  (`PR #598 <https://github.com/eclipse-score/baselibs/pull/598>`__). Use the
  replacement targets.
- ``score::flatbuffers::LoadBuffer`` now takes ``score::cpp::pmr::vector<uint8_t>``
  instead of ``std::pmr::vector<uint8_t>``
  (`PR #603 <https://github.com/eclipse-score/baselibs/pull/603>`__).

These are public APIs of Baselibs; the configuration of the reference
integration does not use them. Action required: adapt own code that uses them.

🎯 Reference Integration scope
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- **Version:** ``v0.10.0``
- **Source / tag:** `Reference integration <https://github.com/eclipse-score/reference_integration/tree/v0.10.0>`__
- **Release notes:** `Reference integration release notes <https://github.com/eclipse-score/reference_integration/releases/tag/v0.10.0>`__
- **Platform Verification Report:** :need:`doc__platform_verification_report_latest`


🧩 Integrated Software Modules
-------------------------------

.. list-table::
   :header-rows: 1
   :widths: 25 15 25 35

   * - Name
     - Version
     - Release notes
     - Module verification report
   * - `Platform <https://github.com/eclipse-score/score/tree/v0.7.2>`__
     - ``v0.7.2``
     - `Release notes <https://github.com/eclipse-score/score/releases/tag/v0.7.2>`__
     - ---
   * - `Baselibs <https://github.com/eclipse-score/baselibs/tree/ee40fece5abacb28ea641b448446a04175038b17>`__
     - ``ee40fec (unreleased)``
     - ---
     - :doc:`Verification report </modules/score_baselibs/verification_report/module_verification_report>`
   * - `Communication <https://github.com/eclipse-score/communication/tree/313f1178628189d267c8cd0d75971bdac04c20ee>`__
     - ``313f117 (unreleased)``
     - ---
     - ---
   * - `Persistency <https://github.com/eclipse-score/persistency/tree/961c0a0989755a1e0fe8de55e83c0a44e2e20b56>`__
     - ``961c0a0 (unreleased)``
     - ---
     - :doc:`Verification report </modules/score_persistency/verification_report/module_verification_report>`
   * - `Kyron <https://github.com/eclipse-score/kyron/tree/90fb90258f49f17a504d41262634d43608f28ccc>`__
     - ``90fb902 (unreleased)``
     - ---
     - ---
   * - `Lifecycle <https://github.com/eclipse-score/lifecycle/tree/85da2168328d17a3cf53791ebf93534e5ed921fc>`__
     - ``85da216 (unreleased)``
     - ---
     - :doc:`Verification report </modules/score_lifecycle/verification_report/index>`
   * - `Logging <https://github.com/eclipse-score/logging/tree/3d9896611baf4e0d018032e5cb999941b2602dbd>`__
     - ``3d98966 (unreleased)``
     - ---
     - :doc:`Verification report </modules/score_logging/verification_report/module_verification_report>`
   * - `Time <https://github.com/eclipse-score/time/tree/3723ce687e4abc7d6cb4c0efdbbd30455ed7c303>`__
     - ``3723ce6 (unreleased)``
     - ---
     - ---
   * - `Configuration Management <https://github.com/eclipse-score/config_management/tree/d0dab01ae408ceb8ec65344e93d8a51d8173da81>`__
     - ``d0dab01 (unreleased)``
     - ---
     - ---

🔧 Associated Infrastructure Modules
-------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 30 25 45

   * - Name
     - Version
     - Release notes
   * - `Crates <https://github.com/eclipse-score/score-crates/tree/v0.0.11>`__
     - ``v0.0.11``
     - `Release notes <https://github.com/eclipse-score/score-crates/releases/tag/v0.0.11>`__
   * - `ITF (Integration Testing Framework) <https://github.com/eclipse-score/itf/tree/v0.6.0>`__
     - ``v0.6.0``
     - `Release notes <https://github.com/eclipse-score/itf/releases/tag/v0.6.0>`__
   * - `Tools <https://github.com/eclipse-score/tools/tree/4b48cec400c67be75cfc3fa4658ac6a0489bf7a8>`__
     - ``4b48cec (unreleased)``
     - ---
   * - `Tooling <https://github.com/eclipse-score/tooling/tree/v2.2.3>`__
     - ``v2.2.3``
     - `Release notes <https://github.com/eclipse-score/tooling/releases/tag/v2.2.3>`__
   * - `Bazel Platforms <https://github.com/eclipse-score/bazel_platforms/tree/v1.1.0>`__
     - ``v1.1.0``
     - `Release notes <https://github.com/eclipse-score/bazel_platforms/releases/tag/v1.1.0>`__
   * - `Test Scenarios <https://github.com/eclipse-score/testing_tools/tree/v0.4.1>`__
     - ``v0.4.1``
     - `Release notes <https://github.com/eclipse-score/testing_tools/releases/tag/v0.4.1>`__
   * - `Docs-as-code <https://github.com/eclipse-score/docs-as-code/tree/v8.4.0>`__
     - ``v8.4.0``
     - `Release notes <https://github.com/eclipse-score/docs-as-code/releases/tag/v8.4.0>`__
   * - `Process description <https://github.com/eclipse-score/process_description/tree/v2.1.2>`__
     - ``v2.1.2``
     - `Release notes <https://github.com/eclipse-score/process_description/releases/tag/v2.1.2>`__
   * - `Bazel CPP Toolchain <https://github.com/eclipse-score/bazel_cpp_toolchains/tree/v1.0.3>`__
     - ``v1.0.3``
     - `Release notes <https://github.com/eclipse-score/bazel_cpp_toolchains/releases/tag/v1.0.3>`__

💿 Images
----------

.. list-table::
   :header-rows: 1
   :widths: 30 15 15 40

   * - Name
     - Tarball
     - How-to
     - Description
   * - Reference Linux x86_64 image
     - ---
     - `How-to <https://github.com/eclipse-score/reference_integration/blob/v0.10.0/README.md#run-showcases>`__
     - Linux x86_64 Docker image bundling the S-CORE showcases.
   * - Reference QNX x86_64 image
     - ---
     - `How-to <https://github.com/eclipse-score/reference_integration/blob/v0.10.0/runners/qemu_x86_64/README.md>`__
     - QNX x86_64 image, run in QEMU.
   * - Reference QNX aarch64 image
     - ---
     - `How-to <https://github.com/eclipse-score/reference_integration/blob/v0.10.0/README.md#build-and-deploy-showcases-on-raspberry-pi-qnx-aarch64>`__
     - QNX 8.0 aarch64 image, run in QEMU or on Raspberry Pi 4/5.
   * - Reference Red Hat AutoSD Linux image (Experimental)
     - ---
     - `How-to <https://github.com/eclipse-score/reference_integration/blob/v0.10.0/README.md#operating-system-integrations>`__
     - Red Hat AutoSD x86_64 image.
   * - Reference Elektrobit corbos Linux for Safety Applications image (Experimental)
     - ---
     - `How-to <https://github.com/eclipse-score/reference_integration/blob/v0.10.0/images/ebclfsa_aarch64/README.md>`__
     - Elektrobit corbos Linux for Safety Applications (aarch64) image.

🐞 Known Issues/Vulnerabilities and Bug Fixes
----------------------------------------------

- See the release notes of the individual modules.

🚀 Upgrade Instructions
------------------------

- Increase to the newest Bazel registry versions: https://eclipse-score.github.io/bazel_registry_ui
- Modules shown as *(unreleased)* are pinned to a commit and have no registry version; use the commit from ``known_good.json``.
- The module versions of this release are listed in `known_good.json <https://github.com/eclipse-score/reference_integration/blob/v0.10.0/known_good.json>`__.


📧 Contact Information
-----------------------

For any questions or support, please contact the *Project leads* or raise an issue/discussion.
https://projects.eclipse.org/projects/automotive.score

