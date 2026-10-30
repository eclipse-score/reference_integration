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
==================================

.. document:: S-CORE v0.10 release note
   :id: doc__score_v010_release_note
   :status: valid
   :safety: QM
   :security: YES
   :realizes: wp__platform_sw_release_note
   :version: 1

| **Platform Release:** S-CORE
| **Release Tag:** v0.10.0
| **Origin Release Tag**: v0.9.0
| **Release Date:** 2026-11-02


Overview
^^^^^^^^

This document provides an overview of the changes, improvements, and bug fixes
included in the software platform release version v0.10.0 as compared to the
previous platform release (v0.9.0).

The v0.10 release replaces the resolved-dependency override mechanism of v0.9
with a two-stage DR-008 test workflow, in which every integrated module is
tested with its own test suite against the unified toolchain configuration of
the reference integration. It adds an SBOM to the build, introduces
showcase-based platform integration tests linked to stakeholder requirements,
extends requirement coverage with module-owned tests, deduplicates the QNX and
Linux image definitions, and updates all integrated modules to their latest
known-good state.

Disclaimer
----------

This release note does not "release for production", as it does not come with a
safety argumentation and a performed safety assessment.
The work products compiled in the safety package are created with care according
to a process satisfying standards, but the project, being a non-profit and open
source organization, can not take over any liability for its content.

Changes to the Platform
^^^^^^^^^^^^^^^^^^^^^^^

New Features
------------

Integration Strategy (DR-008) Test Workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The DR-008 implementation was reworked into a two-stage test workflow:

- **Stage 1** builds and tests the reference integration with all modules as
  pinned in ``known_good.json``.
- **Stage 2** runs the test suite of each target software module on its own,
  with the known-good versions injected via ``--override_module`` and the
  toolchains and platforms shared through ``bazel_common/unified.bazelrc`` and
  ``bazel_common/unified_toolchains.MODULE.bazel``.

The new ``scripts/module_tests.py`` and the ``module_tests.yml`` workflow make
this available for pull requests. Under ``bazel coverage`` the unified
configuration uses clang (LLVM) as C++ toolchain, while builds stay on GCC.
Module-specific exclusions are documented in the new ``metadata.test_notes``
field of ``known_good.json``.

The resolved-dependency override mechanism introduced in v0.9
(``scripts/known_good/resolved_dependencies.py``) was removed in favour of this
workflow.

Software Bill of Materials (SBOM)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The reference integration now generates an SBOM via
`score_sbom <https://github.com/eclipse-score/sbom>`_ (``0.1.1``). All target
software modules are tracked and the SBOM is uploaded as a CI build artifact.

Platform Integration Tests
~~~~~~~~~~~~~~~~~~~~~~~~~~

A new ``platform_integration_tests/`` package runs the ``//showcases`` demo
applications for Communication, Kyron, Lifecycle, Logging and Time as ITF
tests. They are linked to the platform stakeholder requirements, which are now
reported in a dedicated "Stakeholder Requirements" chapter of the platform
verification report.

Improvements
------------

Requirement Coverage from Module Tests
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Lifecycle integration tests, the Logging component tests and the Persistency
component integration tests are now executed by the reference integration, so
their ``PartiallyVerifies``/``FullyVerifies`` links appear in the verification
reports. The Logging integration tests were re-enabled after fixing the
datarouter configuration packaging.

Reference Images
~~~~~~~~~~~~~~~~

- ``score_rules_imagefs`` was updated from ``0.0.1`` to ``0.1.0``, migrating the
  image definitions to ``rules_pkg`` ``pkg_files``.
- QNX and Linux image definitions were deduplicated into shared packages
  (``//images/common/apps``, ``//images/qnx_common/build``,
  ``//images/qnx_common/configs``).

Documentation
~~~~~~~~~~~~~

- Documentation is now generated from ``known_good.json``
  (``bazel_common/docs_bundles.bzl``); the Time documentation bundle was
  enabled.
- The verification report was restructured: the former platform verification
  report page became the status dashboard, module verification reports
  (Lifecycle, Logging, Persistency, ...) are linked from a common index, and
  unit test and coverage summaries are nested under the Platform Verification
  Report.

CI
~~

- The documentation build runs as a separate, fail-fast workflow.
- Bazel cache keys rotate on module bumps; the test cache is trusted on push
  and fresh runs are gated on tags.
- Failing module tests are reported by module name.
- Dashboard documentation links are branch-aware.

Incompatible Changes
--------------------

.. warning::

   The resolved-dependency override mechanism introduced in v0.9
   (``scripts/known_good/resolved_dependencies.py``) and the ``rust_coverage``
   package were removed. Users relying on them need to switch to the DR-008
   test workflow (``scripts/module_tests.py``) and the unified configuration
   in ``bazel_common/unified.bazelrc``.

S-CORE Platform scope
^^^^^^^^^^^^^^^^^^^^^

- **Version:** ``6d65a262c232`` (commit)
- **Release notes**: `S-CORE platform release notes
  <https://github.com/eclipse-score/score/releases>`_

Integrated Software Modules
---------------------------

Baselibs
~~~~~~~~

- ...

Communication
~~~~~~~~~~~~~

- ...

Persistency
~~~~~~~~~~~

- ...

Lifecycle
~~~~~~~~~

- ...

Logging
~~~~~~~

- ...

Time
~~~~

- ...

Configuration Management
~~~~~~~~~~~~~~~~~~~~~~~~

- ...

Kyron
~~~~~

- ...

Reference integration
~~~~~~~~~~~~~~~~~~~~~

- **Version:** ``v0.10.0``
- **Source / tag:** `Reference integration releases
  <https://github.com/eclipse-score/reference_integration/releases>`_

- Added the two-stage DR-008 test workflow and removed the resolved-dependency
  override mechanism.
- Added SBOM generation.
- Added showcase-based platform integration tests.
- Executed Lifecycle, Logging and Persistency module tests for requirement
  coverage.
- Deduplicated QNX/Linux image definitions.

Reference QNX image
+++++++++++++++++++

- Image definitions migrated to ``score_rules_imagefs`` ``0.1.0`` and
  deduplicated between ``qnx_x86_64`` and ``qnx_aarch64``.

Reference Red Hat AutoSD Linux image (Experimental)
+++++++++++++++++++++++++++++++++++++++++++++++++++

- Updated to a newer AutoSD OCI image.

Reference Elektrobit corbos Linux for Safety Applications Linux image (Experimental)
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

- No functional changes in this release.

Associated Infrastructure Modules
---------------------------------

Process description
~~~~~~~~~~~~~~~~~~~

- **Version:** ``2.2.2`` (previously ``2.1.2``)
- **Release notes**: `Process description releases
  <https://github.com/eclipse-score/process_description/releases>`_

Docs-as-code
~~~~~~~~~~~~

- ...


Tooling
~~~~~~~

- ...


Tools
~~~~~

- ...

Platform
~~~~~~~~

- ...

ITF (Integration Testing Framework)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- ...

Test Scenarios
~~~~~~~~~~~~~~

- ...

Crates
~~~~~~

- ...

Bazel CPP Toolchain
~~~~~~~~~~~~~~~~~~~

- ...

Bazel Platforms
~~~~~~~~~~~~~~~

- ...

Compatibility
^^^^^^^^^^^^^

- **Dependencies:** See `Incompatible Changes`_.

Performed Verification
^^^^^^^^^^^^^^^^^^^^^^

- See latest verification: :need:`doc__platform_verification_report_latest`.

Known Issues/Vulnerabilities and Bug Fixes
------------------------------------------

- See release notes of every module separately.
- Several modules are integrated from commit hashes instead of published
  registry releases.
- Some module tests are excluded or relaxed under the clang coverage toolchain
  (Time, Baselibs, Lifecycle); see ``metadata.test_notes`` in
  ``known_good.json``.
- The reference integration carries integration patches for Baselibs,
  Communication, Configuration Management, Lifecycle, Logging, Persistency,
  Platform, Time and ``rules_rust``. See the ``patches/`` directory for details.

Upgrade Instructions
--------------------

- Increase to newest bazel registry versions:
  https://eclipse-score.github.io/bazel_registry_ui
- Versions can be found under:
  https://github.com/eclipse-score/reference_integration/blob/v0.10.0/known_good.json

Contact Information
-------------------

For any questions or support, please contact the *Project leads* or raise an
issue/discussion.
https://projects.eclipse.org/projects/automotive.score
