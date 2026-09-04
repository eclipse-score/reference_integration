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

S-CORE Platform v0.9 release note
=================================

.. document:: S-CORE v0.9 release note
   :id: doc__score_v09_release_note
   :status: draft
   :safety: QM
   :security: YES
   :realizes: wp__platform_sw_release_note
   :version: 1

| **Platform Release:** S-CORE
| **Release Tag:** v0.9.0
| **Origin Release Tag**: v0.8.0
| **Release Date:** 2026-09-07


Overview
^^^^^^^^

This document provides an overview of the changes, improvements, and bug fixes
included in the software platform release version v0.9.0 as compared to the
previous platform release (v0.8.0).

The v0.9 release integrates the Configuration Management module into the
platform for the first time, implements the common integration strategy defined
in DR-008 by means of a resolved-dependency override mechanism, and brings a
broad update of all integrated software and infrastructure modules. It also
carries two module renames that require action from downstream users.

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

Configuration Management
~~~~~~~~~~~~~~~~~~~~~~~~

The `Configuration Management
<https://github.com/eclipse-score/config_management>`_ module has been
integrated into the reference integration for the first time. It provides a
configuration daemon and a proxy API for platform-wide configuration handling.

Logging Demo Application
~~~~~~~~~~~~~~~~~~~~~~~~

A logging demo application was added to the reference integration, demonstrating
the use of the `Logging <https://github.com/eclipse-score/logging>`_ module in
an integrated setting.

Improvements
------------

Integration Strategy (DR-008)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The common integration strategy documented in DR-008, which was aligned during
v0.8, has been implemented: the reference integration gained a
resolved-dependency override mechanism. This allows the integration to steer
transitive module dependency resolution centrally from ``known_good.json``,
instead of relying on the pinning inside each individual module.

Reproducible Dependency Pinning
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The known-good dependency handling was hardened:

- The tag-to-hash resolution was fixed.
- CI checkouts are now pinned to explicit commit hashes.
- ``known_good.json`` now supports pinning a module either by registry
  ``version`` (``single_version_override``) or by ``hash`` (``git_override``),
  which allows integrating modules that have not been released to the registry
  yet.

Build Environment
~~~~~~~~~~~~~~~~~

- Bazel was updated to ``8.6.0``.
- The obsolete AutoSD toolchain usage was removed.

Documentation
~~~~~~~~~~~~~

The reference integration ``README`` was refreshed to give a clearer entry point
into the repository.

Incompatible Changes
--------------------

.. warning::

   This release contains two module renames. Downstream users referencing these
   modules in their own ``MODULE.bazel`` need to adapt their dependencies:

   - ``score_lifecycle_health`` was renamed to ``score_lifecycle``.
   - ``score_process`` was renamed to ``score_process_description``.

   In addition, ``score_bazel_platforms`` was raised to its first major version
   ``1.0.0``, and ``score_docs_as_code`` moved from ``4.6.1`` to ``8.1.1``,
   both of which contain breaking changes.

S-CORE Platform scope
^^^^^^^^^^^^^^^^^^^^^

- **Version:** ``v0.7.2``
- **Release notes**: `S-CORE platform release notes
  <https://github.com/eclipse-score/score/releases>`_

Integrated Software Modules
---------------------------

Baselibs
~~~~~~~~

- **Version:** ``0.2.12`` (previously ``0.2.9``)
- **Release notes**: `Baselibs releases
  <https://github.com/eclipse-score/baselibs/releases>`_

- The QNX8 poll workaround originally carried by Communication is now applied to
  Baselibs as an integration patch.

Communication
~~~~~~~~~~~~~

- **Version:** ``0.4.0`` (previously ``0.3.0``)
- **Release notes**: `Communication releases
  <https://github.com/eclipse-score/communication/releases>`_

- The ``use_typedshmd`` shared-memory flag moved from Baselibs to Communication.

Persistency
~~~~~~~~~~~

- **Version:** ``0.3.5`` (previously ``0.3.4``)
- **Release notes**: `Persistency releases
  <https://github.com/eclipse-score/persistency/releases>`_

Lifecycle
~~~~~~~~~

- **Version:** ``0.6.1`` (previously ``0.3.0``)
- **Release notes**: `Lifecycle releases
  <https://github.com/eclipse-score/lifecycle/releases>`_

- The module was renamed from ``score_lifecycle_health`` to ``score_lifecycle``.

Logging
~~~~~~~

- **Version:** ``0.2.4`` (previously ``0.2.2``)
- **Release notes**: `Logging releases
  <https://github.com/eclipse-score/logging/releases>`_

Time
~~~~

- **Version:** ``0.0.2`` (previously ``0.0.1``)
- **Release notes**: `Time releases
  <https://github.com/eclipse-score/time/releases>`_

Configuration Management
~~~~~~~~~~~~~~~~~~~~~~~~

- **Version:** ``0.2.0`` (newly integrated)
- **Release notes**: `Configuration Management releases
  <https://github.com/eclipse-score/config_management/releases>`_

Orchestrator
~~~~~~~~~~~~

- **Version:** ``0.1.1`` (unchanged)
- **Release notes**: `Orchestrator releases
  <https://github.com/eclipse-score/orchestrator/releases>`_

.. note::

   The v0.8 release note announced that the Orchestrator would be archived in
   v0.9. The module is still integrated at ``0.1.1``; the archival decision
   needs to be confirmed before this release note is finalized.

Kyron
~~~~~

- **Version:** ``0.1.3`` (unchanged)
- **Release notes**: `Kyron releases
  <https://github.com/eclipse-score/kyron/releases>`_

Reference integration
~~~~~~~~~~~~~~~~~~~~~

- **Version:** ``v0.9.0``
- **Source / tag:** `Reference integration releases
  <https://github.com/eclipse-score/reference_integration/releases>`_

- Added a resolved-dependency override mechanism implementing DR-008.
- Integrated the Configuration Management module.
- Added a logging demo application.
- Updated Bazel to ``8.6.0``.
- Hardened known-good dependency handling (tag-to-hash resolution fix,
  hash-pinned CI checkouts).
- Removed the obsolete AutoSD toolchain usage.

Reference QNX image
+++++++++++++++++++

- No functional changes in this release; TBD.

Reference Red Hat AutoSD Linux image (Experimental)
+++++++++++++++++++++++++++++++++++++++++++++++++++

- Removed the obsolete AutoSD toolchain usage from the image build flow.

Reference Elektrobit corbos Linux for Safety Applications Linux image (Experimental)
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

- No functional changes in this release; TBD.

Associated Infrastructure Modules
---------------------------------

Process description
~~~~~~~~~~~~~~~~~~~

- **Version:** ``2.1.2`` (previously ``2.0.1``)
- **Release notes**: `Process description releases
  <https://github.com/eclipse-score/process_description/releases>`_

- The module was renamed from ``score_process`` to
  ``score_process_description``.

Docs-as-code
~~~~~~~~~~~~

- **Version:** ``8.1.1`` (previously ``4.6.1``)
- **Release notes**: `docs-as-code releases
  <https://github.com/eclipse-score/docs-as-code/releases>`_

Tooling
~~~~~~~

- **Version:** ``2.0.2`` (previously ``1.3.1``)
- **Release notes**: `Tooling releases
  <https://github.com/eclipse-score/tooling/releases>`_

- Pinned to ``2.0.2`` with an integration patch in order to keep
  ``rust_coverage_report`` working.

Platform
~~~~~~~~

- **Version:** ``0.7.1`` (previously ``0.6.2``)
- **Release notes**: `Platform releases
  <https://github.com/eclipse-score/score/releases>`_

ITF (Integration Testing Framework)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Version:** ``0.5.0`` (previously ``0.3.0``)
- **Release notes**: `ITF releases
  <https://github.com/eclipse-score/itf/releases>`_

Test Scenarios
~~~~~~~~~~~~~~

- **Version:** ``0.4.1`` (unchanged)
- **Release notes**: `Test Scenarios releases
  <https://github.com/eclipse-score/testing_tools/releases>`_

Crates
~~~~~~

- **Version:** ``0.0.11`` (previously ``0.0.10``)
- **Release notes**: `Crates releases
  <https://github.com/eclipse-score/score-crates/releases>`_

Bazel CPP Toolchain
~~~~~~~~~~~~~~~~~~~

- **Version:** ``0.5.4``
- **Release notes**: `Bazel CPP Toolchain releases
  <https://github.com/eclipse-score/bazel_cpp_toolchains/releases>`_

Bazel Platforms
~~~~~~~~~~~~~~~

- **Version:** ``1.0.0`` (previously ``0.1.2``)
- **Release notes**: `Bazel Platforms releases
  <https://github.com/eclipse-score/bazel_platforms/releases>`_


Compatibility
^^^^^^^^^^^^^

- **Dependencies:** See the module renames and major version bumps listed under
  `Incompatible Changes`_.

Performed Verification
^^^^^^^^^^^^^^^^^^^^^^

- See latest verification: :need:`doc__platform_verification_report_latest`.

Known Issues/Vulnerabilities and Bug Fixes
------------------------------------------

- See release notes of every module separately.
- All modules listed here are integrated from published registry releases.
- The reference integration carries integration patches for Baselibs,
  Communication, Configuration Management, Logging, Time and Tooling. See the
  ``patches/`` directory for details.

Upgrade Instructions
--------------------

- Increase to newest bazel registry versions:
  https://eclipse-score.github.io/bazel_registry_ui
- Versions can be found under:
  https://github.com/eclipse-score/reference_integration/blob/v0.9.0/known_good.json
- Rename the module dependencies ``score_lifecycle_health`` to
  ``score_lifecycle`` and ``score_process`` to ``score_process_description`` in
  your ``MODULE.bazel``.

Contact Information
-------------------

For any questions or support, please contact the *Project leads* or raise an
issue/discussion.
https://projects.eclipse.org/projects/automotive.score
