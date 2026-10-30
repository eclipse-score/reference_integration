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

S-CORE Platform v0.10 release note (DRAFT)
============================================

.. warning::

   **DRAFT - release in progress.** v0.10.0 is not released yet (planned for
   2026-11-02). This note shows the current state of the integration and changes
   until the release is published.


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

.. figure:: /s_core_v_1/releases/_assets/architecture_v0_10.svg
   :width: 100%
   :alt: S-CORE v0.10 reference integration architecture

   Modules, components and images of the reference integration v0.10.0.


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

New infrastructure module: Tools
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``score_tools`` (`eclipse-score/tools <https://github.com/eclipse-score/tools>`__)
is now part of ``known_good.json``. Persistency's test BUILD files load
``@score_tools//score_pytest``, so the reference integration needs it as a
regular dependency
(`#388 <https://github.com/eclipse-score/reference_integration/pull/388>`__).

Integration Strategy (DR-008) test workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The reference integration no longer runs the unit tests of all modules inside
its own workspace. Each target software module now runs its own test suite in
its own workspace, against the dependency versions resolved by the reference
integration
(`#398 <https://github.com/eclipse-score/reference_integration/pull/398>`__):

- ``scripts/module_tests.py run <module>`` fetches the module at its
  ``known_good.json`` pin with the integration patches applied, pins its direct
  dependencies to the versions of the reference integration
  (``--override_module``) and runs ``bazel coverage`` with the shared
  configuration from ``bazel_common/unified.bazelrc`` and
  ``bazel_common/unified_toolchains.MODULE.bazel``. Coverage builds C++ with
  clang (LLVM); regular builds stay on GCC.
- The ``module_tests.yml`` workflow runs one job per module and feeds the
  results into the unit test summary and the documentation.
- Module-specific test exclusions are documented in the ``metadata.test_notes``
  field of ``known_good.json``.
- If the ``UBUNTU_SNAPSHOT_MIRROR_URL`` secret is set, the module test jobs
  download Ubuntu snapshot packages from a mirror first
  (`#429 <https://github.com/eclipse-score/reference_integration/pull/429>`__).

Software Bill of Materials (SBOM)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The reference integration generates an SBOM with
`score_sbom <https://github.com/eclipse-score/sbom>`__ ``0.1.1`` and uploads it
as a CI build artifact
(`#304 <https://github.com/eclipse-score/reference_integration/pull/304>`__,
`#339 <https://github.com/eclipse-score/reference_integration/pull/339>`__,
`#353 <https://github.com/eclipse-score/reference_integration/pull/353>`__).

Reference images
~~~~~~~~~~~~~~~~

- The QNX images use ``score_rules_imagefs`` ``0.1.0``; host files are placed
  with ``rules_pkg`` ``pkg_files`` targets
  (`#349 <https://github.com/eclipse-score/reference_integration/pull/349>`__).
- The QNX and Linux image definitions were deduplicated into shared packages:
  ``//images/common/apps``, ``//images/qnx_common/build`` and
  ``//images/qnx_common/configs``
  (`#389 <https://github.com/eclipse-score/reference_integration/pull/389>`__).
- The AutoSD image uses a newer AutoSD OCI base image and is pushed on release
  (`#404 <https://github.com/eclipse-score/reference_integration/pull/404>`__,
  `#424 <https://github.com/eclipse-score/reference_integration/pull/424>`__).

Platform integration tests
~~~~~~~~~~~~~~~~~~~~~~~~~~

The new ``//platform_integration_tests:pit`` suite runs the ``//showcases``
applications for Communication, Kyron, Lifecycle, Logging and Time on the target
image (Docker on Linux x86_64, QEMU on QNX x86_64). Each test is linked to the
platform stakeholder requirement it demonstrates; the platform verification
report shows them in a new "Stakeholder Requirements" chapter
(`#377 <https://github.com/eclipse-score/reference_integration/pull/377>`__).

Requirement coverage from module tests
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Lifecycle integration tests, the Logging component tests and the Persistency
component integration tests are executed by the reference integration, so their
``PartiallyVerifies``/``FullyVerifies`` links appear in the verification reports
(`#385 <https://github.com/eclipse-score/reference_integration/pull/385>`__).
The Logging tests run after fixing the packaging of the datarouter
configuration
(`#387 <https://github.com/eclipse-score/reference_integration/pull/387>`__).

Lifecycle control interface for State Managers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Lifecycle provides the new ``ILmControl`` API, with which State Managers
communicate with the Launch Manager over ``mw::com``
(`Lifecycle v0.8.0 release notes <https://github.com/eclipse-score/lifecycle/releases/tag/v0.8.0>`__).

Documentation and reports
~~~~~~~~~~~~~~~~~~~~~~~~~

- The documentation bundles are generated from ``known_good.json``
  (``bazel_common/docs_bundles.bzl``); the Time documentation is included
  (`#337 <https://github.com/eclipse-score/reference_integration/pull/337>`__,
  `#348 <https://github.com/eclipse-score/reference_integration/pull/348>`__).
- Module verification reports (Baselibs, Lifecycle, Logging, Persistency) are
  linked from a common index; the unit test and coverage summaries are part of
  the Platform Verification Report; the status dashboard uses branch-aware links
  (`#342 <https://github.com/eclipse-score/reference_integration/pull/342>`__,
  `#358 <https://github.com/eclipse-score/reference_integration/pull/358>`__,
  `#373 <https://github.com/eclipse-score/reference_integration/pull/373>`__).
- The Overall Status page was replaced by the Release-wide Progress Overview
  next to the release notes, with release-over-release charts per module
  (`#392 <https://github.com/eclipse-score/reference_integration/pull/392>`__).
- The release note is generated from ``known_good.json`` with
  ``scripts/release_note/generate_release_note.py``
  (`#414 <https://github.com/eclipse-score/reference_integration/pull/414>`__).

CI
~~

- The documentation build runs as a separate, fail-fast workflow
  (`#375 <https://github.com/eclipse-score/reference_integration/pull/375>`__).
- Bazel cache keys rotate on module bumps and the test cache is trusted on push
  (`#356 <https://github.com/eclipse-score/reference_integration/pull/356>`__,
  `#362 <https://github.com/eclipse-score/reference_integration/pull/362>`__,
  `#366 <https://github.com/eclipse-score/reference_integration/pull/366>`__).
- Failing module tests are reported by module name
  (`#368 <https://github.com/eclipse-score/reference_integration/pull/368>`__).

💥 Breaking Changes
--------------------

Reference integration: resolved-dependency overrides removed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The module test mechanism of v0.9 was removed together with its generated files:
``scripts/known_good/resolved_dependencies.py``,
``scripts/known_good/module_patches.py`` and the ``rust_coverage`` package
(`#398 <https://github.com/eclipse-score/reference_integration/pull/398>`__).

Action required: run module tests with ``scripts/module_tests.py`` and the
configuration in ``bazel_common/unified.bazelrc`` instead.

Reference integration: QNX image packages moved
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The common QNX build fragments and configuration files moved to
``//images/qnx_common/build`` and ``//images/qnx_common/configs``; the
``images/qnx_aarch64/configs`` package was removed and
``images/qnx_x86_64/configs`` keeps only the x86-specific files
(`#389 <https://github.com/eclipse-score/reference_integration/pull/389>`__).

Action required: update references to the old image paths in derived images.

Platform: stakeholder requirement IDs renamed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Platform ``v0.7.4`` renamed ``stkh_req__dependability__safety_features_1`` to
``stkh_req__dependability__health_management``. Tests that still link the old
ID make the documentation build fail with an unknown-link warning
(`5d09c1b <https://github.com/eclipse-score/reference_integration/commit/5d09c1bf631767564295ee403d200d2f201eb76a>`__,
`Platform v0.7.4 release notes <https://github.com/eclipse-score/score/releases/tag/v0.7.4>`__).

Action required: link tests to the new stakeholder requirement IDs.

Baselibs: vaJson is the only JSON backend
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``score/json`` uses vaJson as its only parser (v0.2.15) and writer (v0.2.16).
The ``--@score_baselibs//score/json:writer_library`` flag was removed;
``--@score_baselibs//score/json:base_library`` is a deprecated no-op that this
repository still sets in ``.bazelrc`` and ``known_good.json``. The written JSON
differs (for example ``true``/``false`` instead of ``1``/``0`` and different
float formatting), which is why two Configuration Management unit tests are
excluded in ``known_good.json``
(`Baselibs v0.2.15 <https://github.com/eclipse-score/baselibs/releases/tag/v0.2.15>`__,
`Baselibs v0.2.16 <https://github.com/eclipse-score/baselibs/releases/tag/v0.2.16>`__,
`312fde3 <https://github.com/eclipse-score/reference_integration/commit/312fde355d1270ab713603ce3233d39c81407c7d>`__).

Action required: remove the ``base_library`` and ``writer_library`` flags from
build configurations and do not compare JSON output against the old format.

Persistency: KVS API and file format
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The integrated Persistency commit changes the public KVS API that applications
use directly:

- ``Kvs::reset_key`` was renamed to ``SetValueToDefault`` (C++) and
  ``set_value_to_default`` (Rust), without a deprecated alias
  (`persistency#585 <https://github.com/eclipse-score/persistency/pull/585>`__,
  `873238a <https://github.com/eclipse-score/reference_integration/commit/873238a8474c470eb571a47abdf25cab382a6a9e>`__,
  `0e4c5be <https://github.com/eclipse-score/reference_integration/commit/0e4c5be3ebb3441d5f25e72772745ea553b01d67>`__).
- The KVS rejects untagged JSON; a defaults file must use the type-tagged
  top-level envelope ``{"t":"obj","v":{...}}``
  (`persistency#490 <https://github.com/eclipse-score/persistency/pull/490>`__,
  `c37c448 <https://github.com/eclipse-score/reference_integration/commit/c37c448bf429d1eb519a5dcff39d61205d73b37c>`__).
- The C++ headers are included as ``score/kvs/kvs.h``, ``kvs_builder.h`` and
  ``kvs_value.h`` from ``@score_persistency//score/kvs``, and the
  ``KvsBuilder`` flags became enums (``Defaults``, ``KvsLoad``,
  ``WorkingDir``). Configuration Management is adapted by a patch in this
  repository
  (`3467044 <https://github.com/eclipse-score/reference_integration/commit/346704410622c0863cbb5cf04a1578f426cf797e>`__).

Action required: rename ``reset_key`` calls, convert defaults files to the
tagged envelope and update the KVS includes and builder calls.

Lifecycle: Launch Manager configuration in milliseconds
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Lifecycle ``v0.9.0`` renamed all duration fields of the Launch Manager
configuration to integer milliseconds, for example ``transition_timeout`` to
``transition_timeout_ms`` and ``reporting_cycle`` to ``reporting_cycle_ms``.
Configurations with the old keys fail the schema validation
(`a575ce6 <https://github.com/eclipse-score/reference_integration/commit/a575ce6982f0d73ed759462f25f29d2d39ab7627>`__,
`Lifecycle v0.9.0 release notes <https://github.com/eclipse-score/lifecycle/releases/tag/v0.9.0>`__).

Action required: rename the duration fields to ``*_ms`` and convert the values
from seconds to milliseconds.

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
   * - `Platform <https://github.com/eclipse-score/score/tree/v0.7.4>`__
     - ``v0.7.4``
     - `Release notes <https://github.com/eclipse-score/score/releases/tag/v0.7.4>`__
     - ---
   * - `Baselibs <https://github.com/eclipse-score/baselibs/tree/v0.2.16>`__
     - ``v0.2.16``
     - `Release notes <https://github.com/eclipse-score/baselibs/releases/tag/v0.2.16>`__
     - :doc:`Verification report </modules/score_baselibs/verification_report/module_verification_report>`
   * - `Communication <https://github.com/eclipse-score/communication/tree/313f1178628189d267c8cd0d75971bdac04c20ee>`__
     - ``313f117 (unreleased)``
     - ---
     - ---
   * - `Persistency <https://github.com/eclipse-score/persistency/tree/41d76090c7d0b05068cdc5bb22ef2e9f3571906a>`__
     - ``41d7609 (unreleased)``
     - ---
     - :doc:`Verification report </modules/score_persistency/verification_report/module_verification_report>`
   * - `Kyron <https://github.com/eclipse-score/kyron/tree/52d4bef3d1822f82199d72e58e815b9e43406fe6>`__
     - ``52d4bef (unreleased)``
     - ---
     - ---
   * - `Lifecycle <https://github.com/eclipse-score/lifecycle/tree/v0.9.0>`__
     - ``v0.9.0``
     - `Release notes <https://github.com/eclipse-score/lifecycle/releases/tag/v0.9.0>`__
     - :doc:`Verification report </modules/score_lifecycle/verification_report/module_verification_report>`
   * - `Logging <https://github.com/eclipse-score/logging/tree/v0.2.5>`__
     - ``v0.2.5``
     - `Release notes <https://github.com/eclipse-score/logging/releases/tag/v0.2.5>`__
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
   * - `Test Scenarios <https://github.com/eclipse-score/testing_tools/tree/v0.5.0>`__
     - ``v0.5.0``
     - `Release notes <https://github.com/eclipse-score/testing_tools/releases/tag/v0.5.0>`__
   * - `Docs-as-code <https://github.com/eclipse-score/docs-as-code/tree/v8.6.0>`__
     - ``v8.6.0``
     - `Release notes <https://github.com/eclipse-score/docs-as-code/releases/tag/v8.6.0>`__
   * - `Process description <https://github.com/eclipse-score/process_description/tree/v2.2.2>`__
     - ``v2.2.2``
     - `Release notes <https://github.com/eclipse-score/process_description/releases/tag/v2.2.2>`__
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

