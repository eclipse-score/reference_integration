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

.. note::

   **FINAL.** This is the release note of release
   `v0.10.0 <https://github.com/eclipse-score/reference_integration/releases/tag/v0.10.0>`__ (2026-11-02).


.. document:: S-CORE v0.10 release note
   :id: doc__score_v010_release_note
   :status: valid
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

The maturity classification of the software modules (Release, Experimental,
Preview) is explained in `DR-003-Strat: Module Maturity Classification <https://github.com/eclipse-score/score/blob/main/docs/design_decisions/strategy/DR-003-strat.md>`__.


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
is part of ``known_good.json``. Persistency's test BUILD files load
``@score_tools//score_pytest``, which moved there from Docs-as-code, so
``reference_integration`` needs it as a regular dependency
(`#388 <https://github.com/eclipse-score/reference_integration/pull/388>`__).

New infrastructure module: Devcontainer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``score_devcontainer`` (`eclipse-score/devcontainer <https://github.com/eclipse-score/devcontainer>`__)
is pinned in ``known_good.json`` at ``1.11.4``; ``scripts/module_tests.py``
raises the modules' own ``score_devcontainer`` dependency to this version
(`#438 <https://github.com/eclipse-score/reference_integration/pull/438>`__).

Bazel 8.8.2
~~~~~~~~~~~

``reference_integration`` builds with Bazel ``8.8.2`` instead of ``8.6.0``
(``.bazelversion``)
(`#436 <https://github.com/eclipse-score/reference_integration/pull/436>`__).

Integration Strategy (DR-008) test workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each target software module runs its own test suite in its own workspace,
against the dependency versions of ``reference_integration``, instead of
inside the workspace of ``reference_integration``. This implements the parts
of DR-008 that the v0.9 release note left for a follow-up release
(`#398 <https://github.com/eclipse-score/reference_integration/pull/398>`__):

- ``scripts/module_tests.py run <module>`` fetches the module at its
  ``known_good.json`` pin with the integration patches, pins its direct
  dependencies to the versions of ``reference_integration``
  (``--override_module``) and runs ``bazel coverage`` with
  ``bazel_common/unified.bazelrc`` and
  ``bazel_common/unified_toolchains.MODULE.bazel``.
- The ``module_tests.yml`` workflow runs one job per module and feeds the
  results into the unit test summary and the documentation.
- Module-specific test exclusions are documented in ``metadata.test_notes`` of
  ``known_good.json``.
- With the secret ``UBUNTU_SNAPSHOT_MIRROR_URL`` the module test jobs download
  Ubuntu snapshot packages from a mirror first
  (`#429 <https://github.com/eclipse-score/reference_integration/pull/429>`__).

Software Bill of Materials (SBOM)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``reference_integration`` generates an SBOM with
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
- The QNX and Linux image definitions share the packages
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
image (Docker on Linux x86_64, QEMU on QNX x86_64). Each test links the platform
stakeholder requirement it demonstrates; the platform verification report shows
them in the chapter "Stakeholder Requirements"
(`#377 <https://github.com/eclipse-score/reference_integration/pull/377>`__).

Requirement coverage from module tests
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``reference_integration`` executes the Lifecycle integration tests, the Logging
component tests and the Persistency component integration tests, so their
``PartiallyVerifies``/``FullyVerifies`` links appear in the verification reports
(`#385 <https://github.com/eclipse-score/reference_integration/pull/385>`__,
`#387 <https://github.com/eclipse-score/reference_integration/pull/387>`__).

Qualified coverage tool in the modules
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Baselibs, Kyron, Persistency and Time measure coverage with the qualified
``score_coverage`` module
(`eclipse-score/coverage_tool <https://github.com/eclipse-score/coverage_tool>`__)
instead of the coverage pipeline of ``score_tooling``. One
``bazel coverage --config=llvm_cov`` run reports line and branch coverage for
C++ and Rust, lists untested files with 0 % and supports coverage
justifications
(`baselibs#584 <https://github.com/eclipse-score/baselibs/pull/584>`__,
`kyron#175 <https://github.com/eclipse-score/kyron/pull/175>`__,
`persistency#450 <https://github.com/eclipse-score/persistency/pull/450>`__,
`time#235 <https://github.com/eclipse-score/time/pull/235>`__).

Lifecycle: control interface for State Managers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Lifecycle provides the ``ILmControl`` API, with which State Managers
communicate with the Launch Manager over ``mw::com``
(`Lifecycle v0.8.0 release notes <https://github.com/eclipse-score/lifecycle/releases/tag/v0.8.0>`__).

Logging: Linux syslog backend
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``mw::log`` has a Linux ``syslog(3)`` backend for ``LogMode::kSystem``, based on
the new ``score::os::Syslog`` wrapper of Baselibs
(`logging#271 <https://github.com/eclipse-score/logging/pull/271>`__,
`baselibs#502 <https://github.com/eclipse-score/baselibs/pull/502>`__).

ITF: QEMU plugin for Linux images
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The QEMU plugin of ITF ``v0.6.0`` boots Linux images in addition to QNX images
(EB corbos Linux for aarch64 and Ubuntu, with image definitions from
``os_images``), accepts an additional disk image with the test binaries and
their data, and has a hook for extra QEMU arguments
(`itf#122 <https://github.com/eclipse-score/itf/pull/122>`__,
`itf#123 <https://github.com/eclipse-score/itf/pull/123>`__,
`itf#135 <https://github.com/eclipse-score/itf/pull/135>`__,
`itf#139 <https://github.com/eclipse-score/itf/pull/139>`__).

Module maturity classification (DR-003)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The architecture diagram shows the maturity of each software module (Release,
Experimental, Preview) as defined in
`DR-003-Strat <https://github.com/eclipse-score/score/blob/main/docs/design_decisions/strategy/DR-003-strat.md>`__.
A module without module verification report and without dependable element
documentation is Preview; a module whose component requirements are all fully
verified and inspected is Release; all other modules are Experimental. This
follows up on the maturity levels announced in the v0.8 release note
(`842d366 <https://github.com/eclipse-score/reference_integration/commit/842d366755c765cc91e8cadcaa5f37799c7e6d06>`__).

Documentation and reports
~~~~~~~~~~~~~~~~~~~~~~~~~

- The documentation bundles are generated from ``known_good.json``
  (``bazel_common/docs_bundles.bzl``); the Time documentation is included
  (`#337 <https://github.com/eclipse-score/reference_integration/pull/337>`__,
  `#348 <https://github.com/eclipse-score/reference_integration/pull/348>`__).
- The module verification reports (Baselibs, Lifecycle, Logging, Persistency)
  are linked from a common index; the unit test and coverage summaries are part
  of the Platform Verification Report; the status dashboard uses branch-aware
  links
  (`#342 <https://github.com/eclipse-score/reference_integration/pull/342>`__,
  `#358 <https://github.com/eclipse-score/reference_integration/pull/358>`__,
  `#373 <https://github.com/eclipse-score/reference_integration/pull/373>`__).
- The Platform Verification Report uses the ``platform_verification_report``
  template of Docs-as-code
  (`Docs-as-code v8.2.0 release notes <https://github.com/eclipse-score/docs-as-code/releases/tag/v8.2.0>`__).
- The module tests export the coverage reports of Baselibs, Persistency,
  Logging, Kyron, Lifecycle and Time and combine them into one LCOV file
  (``coverage-report/coverage_report.dat``) that the documentation build reads;
  Communication and Configuration Management run their tests without coverage
  (`#425 <https://github.com/eclipse-score/reference_integration/pull/425>`__).
- The documentation of the Communication dependable elements is published via
  the module test artifacts and linked from the module documentation index
  (``metadata.dependable_element_docs`` in ``known_good.json``)
  (`bbf95e3 <https://github.com/eclipse-score/reference_integration/commit/bbf95e3d9fce50d8135e90bb89f7c0f2e096cac3>`__,
  `d612b38 <https://github.com/eclipse-score/reference_integration/commit/d612b38c4a4fed4863f08ac33ee9c7c4b7249952>`__).
- The Overall Status page was replaced by the Release-wide Progress Overview
  next to the release notes, with release-over-release charts per module
  (`#392 <https://github.com/eclipse-score/reference_integration/pull/392>`__).
- The release note is generated with
  ``scripts/release_note/generate_release_note.py``; its module tables link
  every module release since the origin release
  (`#414 <https://github.com/eclipse-score/reference_integration/pull/414>`__,
  `cf0f846 <https://github.com/eclipse-score/reference_integration/commit/cf0f846361955740dbf8e84029be35dad6afbc9f>`__).

CI
~~

- The documentation build runs as a separate, fail-fast workflow
  (`#375 <https://github.com/eclipse-score/reference_integration/pull/375>`__).
- Bazel cache keys rotate on module bumps, and the test cache is trusted on push
  (`#356 <https://github.com/eclipse-score/reference_integration/pull/356>`__,
  `#362 <https://github.com/eclipse-score/reference_integration/pull/362>`__,
  `#366 <https://github.com/eclipse-score/reference_integration/pull/366>`__).
- Failing module tests are reported by module name
  (`#368 <https://github.com/eclipse-score/reference_integration/pull/368>`__).

💥 Breaking Changes
--------------------

reference_integration: resolved-dependency overrides removed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The module test mechanism of v0.9 was removed with its files
``scripts/known_good/resolved_dependencies.py``,
``scripts/known_good/module_patches.py`` and the ``rust_coverage`` package
(`#398 <https://github.com/eclipse-score/reference_integration/pull/398>`__).

Action required: run module tests with ``scripts/module_tests.py`` and the
configuration in ``bazel_common/unified.bazelrc``.

reference_integration: QNX image packages moved
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The common QNX build fragments and configuration files moved to
``//images/qnx_common/build`` and ``//images/qnx_common/configs``; the package
``images/qnx_aarch64/configs`` was removed and ``images/qnx_x86_64/configs``
keeps only the x86-specific files
(`#389 <https://github.com/eclipse-score/reference_integration/pull/389>`__).

Action required: update references to the old image paths in derived images.

Platform: stakeholder requirement IDs renamed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Platform ``v0.7.3`` gives the safety stakeholder requirements named IDs
instead of numbers, for example ``stkh_req__dependability__safety_features_1``
became ``stkh_req__dependability__health_management``. Tests that still link an
old ID make the documentation build fail with an unknown-link warning
(`score#3286 <https://github.com/eclipse-score/score/pull/3286>`__).

.. note::

   Important for integrators: the Lifecycle platform integration test of
   ``reference_integration`` links the renamed requirement
   (`5d09c1b <https://github.com/eclipse-score/reference_integration/commit/5d09c1bf631767564295ee403d200d2f201eb76a>`__).

Action required: link tests to the new stakeholder requirement IDs.

Baselibs: vaJson is the only JSON backend
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``score/json`` uses vaJson as its only parser and writer; ``JsonParser``,
``IJsonParser`` and ``JsonWriter`` keep their interfaces:

- v0.2.15: the nlohmann parser was removed together with the
  ``nlohmann_json`` dependency of Baselibs; the flag
  ``--@score_baselibs//score/json:base_library`` is a deprecated no-op, also
  with the value ``nlohmann``
  (`baselibs#660 <https://github.com/eclipse-score/baselibs/pull/660>`__).
- v0.2.16: the flag ``--@score_baselibs//score/json:writer_library`` and the
  ``json_serialize`` writer were removed. The written JSON differs, for example
  ``true``/``false`` instead of ``1``/``0`` and a different float format; the
  enum ``Formatting`` moved to ``score/json/formatting.h``
  (`baselibs#675 <https://github.com/eclipse-score/baselibs/pull/675>`__,
  `baselibs#685 <https://github.com/eclipse-score/baselibs/pull/685>`__).
- v0.2.17: the class ``VajsonParser`` and the target ``vajson_parser`` were
  removed
  (`baselibs#677 <https://github.com/eclipse-score/baselibs/pull/677>`__).

.. note::

   Important for integrators: ``reference_integration`` still sets
   ``base_library=nlohmann`` in ``.bazelrc`` and ``known_good.json``; the flag
   has no effect. Two Configuration Management unit tests are excluded in
   ``known_good.json`` because their expected strings assume the nlohmann float
   format (``3.222`` instead of ``3.22199988``)
   (`312fde3 <https://github.com/eclipse-score/reference_integration/commit/312fde355d1270ab713603ce3233d39c81407c7d>`__).

Action required: remove the ``base_library`` and ``writer_library`` flags, use
``JsonParser`` instead of ``VajsonParser``, include ``score/json/formatting.h``
for ``Formatting`` and do not compare JSON output with the old format.

Baselibs: deprecated APIs and targets removed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Baselibs removed deprecated or unused APIs; Persistency and Logging migrated
away from them
(`persistency#455 <https://github.com/eclipse-score/persistency/pull/455>`__,
`logging#343 <https://github.com/eclipse-score/logging/pull/343>`__):

- ``score::Blank``, ``score::ResultBlank`` and the macros ``STRUCT_VISITABLE``,
  ``STRUCT_TRACEABLE``, ``MEMCPY_SERIALIZABLE`` and ``MEMCPY_SERIALIZABLE_IF``
  (v0.2.16)
  (`baselibs#623 <https://github.com/eclipse-score/baselibs/pull/623>`__).
- The ``//src`` aliases and the string and atomic shims in ``//score/memory``
  (v0.2.14)
  (`baselibs#598 <https://github.com/eclipse-score/baselibs/pull/598>`__).
- ``//score/datetime_converter`` and the ``score/os`` cpuid, file stream,
  make-dev and ``select`` wrappers (v0.2.13), the Linux
  ``pthread_setaffinity_np`` wrapper and the deprecated QNX ``ChannelCreate``
  and ``TimerTimeout`` overloads (v0.2.16)
  (`baselibs#471 <https://github.com/eclipse-score/baselibs/pull/471>`__,
  `baselibs#535 <https://github.com/eclipse-score/baselibs/pull/535>`__,
  `baselibs#536 <https://github.com/eclipse-score/baselibs/pull/536>`__,
  `baselibs#703 <https://github.com/eclipse-score/baselibs/pull/703>`__).
- Deprecated: ``Synchronized::WithLock``, replaced by the monadic functions of
  ``LockedPtr`` (v0.2.17)
  (`baselibs#761 <https://github.com/eclipse-score/baselibs/pull/761>`__).

Action required: use ``void``/``score::Result<void>`` and the ``SCORE_*``
macros, depend on the ``//score`` targets and replace the removed OS wrappers
and ``WithLock``.

Communication: removed deprecated API and exception specifications
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Communication ``v0.5.0`` and ``v0.6.0`` change public ``mw::com`` APIs that
applications use directly
(`Communication v0.5.0 release notes <https://github.com/eclipse-score/communication/releases/tag/v0.5.0>`__,
`Communication v0.6.0 release notes <https://github.com/eclipse-score/communication/releases/tag/v0.6.0>`__):

- ``GenericProxyEvent::GetSampleSize()``, deprecated in ``v0.5.0``, was removed
  in ``v0.6.0``; use ``GetDataTypeSizeInfo().Size()``
  (`communication#997 <https://github.com/eclipse-score/communication/pull/997>`__).
- Functions that can propagate exceptions are no longer ``noexcept``:
  ``GenericProxyEvent::SetReceiveHandler``, ``UnsetReceiveHandler`` and
  ``Unsubscribe`` (``v0.5.0``), ``GenericSkeleton::StopOfferService()``,
  ``GenericSkeletonEvent::Send()`` and ``GenericSkeletonEvent::Notify()``
  (``v0.6.0``)
  (`communication#1202 <https://github.com/eclipse-score/communication/pull/1202>`__,
  `communication#1232 <https://github.com/eclipse-score/communication/pull/1232>`__).
- ``tracing::TypeErasedSamplePtr`` was replaced by ``impl::SamplePtr<void>``
  (``v0.5.0``)
  (`communication#1229 <https://github.com/eclipse-score/communication/pull/1229>`__).
- The aggregate Bazel target ``//score/memory/shared:types`` was removed
  (``v0.6.0``)
  (`communication#1487 <https://github.com/eclipse-score/communication/pull/1487>`__).

Action required: replace ``GetSampleSize()`` and ``TypeErasedSamplePtr``, do
not rely on ``noexcept`` of the listed functions and depend on the specific
``//score/memory/shared`` sub-targets (for example ``:offset_ptr``,
``:vector``, ``:string``).

Persistency: KVS API and file format
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Persistency ``v0.4.0`` changes the public KVS API that applications use
directly
(`Persistency v0.4.0 release notes <https://github.com/eclipse-score/persistency/releases/tag/v0.4.0>`__):

- ``Kvs::reset_key`` was renamed to ``SetValueToDefault`` (C++) and
  ``set_value_to_default`` (Rust), without a deprecated alias
  (`persistency#585 <https://github.com/eclipse-score/persistency/pull/585>`__).
- The KVS rejects untagged JSON; a defaults file must use the type-tagged
  top-level envelope ``{"t":"obj","v":{...}}``
  (`persistency#490 <https://github.com/eclipse-score/persistency/pull/490>`__).
- The C++ headers are ``score/kvs/kvs.h``, ``kvs_builder.h`` and
  ``kvs_value.h`` in ``@score_persistency//score/kvs`` and are included with the
  full path; the ``KvsBuilder`` flags became enums (``Defaults``, ``KvsLoad``,
  ``WorkingDir``)
  (`persistency#461 <https://github.com/eclipse-score/persistency/pull/461>`__,
  `persistency#562 <https://github.com/eclipse-score/persistency/pull/562>`__).
- Deprecated, still available: the namespace ``score::mw::per::kvs`` (now
  ``score::kvs``), the old ``*.hpp`` headers, the snake_case method names (now
  PascalCase) and constants and enumerators without ``k`` prefix
  (`persistency#562 <https://github.com/eclipse-score/persistency/pull/562>`__,
  `persistency#564 <https://github.com/eclipse-score/persistency/pull/564>`__,
  `persistency#614 <https://github.com/eclipse-score/persistency/pull/614>`__).
- Keys must be non-empty, consist of printable ASCII characters and be at most
  32 bytes long; the C++ and Rust KVS return ``InvalidKey`` for other keys, and
  loading a file with such a key fails
  (`persistency#308 <https://github.com/eclipse-score/persistency/pull/308>`__,
  `persistency#508 <https://github.com/eclipse-score/persistency/pull/508>`__,
  `persistency#509 <https://github.com/eclipse-score/persistency/pull/509>`__).
- The KVS stores its files atomically with the permissions ``640``
  (`persistency#503 <https://github.com/eclipse-score/persistency/pull/503>`__).

.. note::

   Important for integrators: ``reference_integration`` adapts Configuration
   Management ``v0.3.1`` to the new headers and builder API by the patch
   ``patches/config_management/002-migrate-to-persistency-kvs-api.patch``
   (`3467044 <https://github.com/eclipse-score/reference_integration/commit/346704410622c0863cbb5cf04a1578f426cf797e>`__).
   The feature integration tests use ``SetValueToDefault`` and
   ``set_value_to_default`` and write the defaults files with the tagged
   envelope
   (`873238a <https://github.com/eclipse-score/reference_integration/commit/873238a8474c470eb571a47abdf25cab382a6a9e>`__,
   `0e4c5be <https://github.com/eclipse-score/reference_integration/commit/0e4c5be3ebb3441d5f25e72772745ea553b01d67>`__,
   `c37c448 <https://github.com/eclipse-score/reference_integration/commit/c37c448bf429d1eb519a5dcff39d61205d73b37c>`__).

Action required: rename ``reset_key`` calls, convert defaults files to the
tagged envelope, update the KVS includes, builder calls and names, keep keys
within the allowed characters and length, and check that processes reading KVS
files of another user still have access.

Lifecycle: Launch Manager configuration and control API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Lifecycle ``v0.7.0`` to ``v0.10.0`` change the Launch Manager configuration
and its control interface. Configurations with old keys fail the schema
validation:

- ``v0.7.0``: all durations are configured in milliseconds, and the keys get
  the suffix ``_ms``, for example ``transition_timeout_ms`` and
  ``reporting_cycle_ms``
  (`lifecycle#637 <https://github.com/eclipse-score/lifecycle/pull/637>`__).
- ``v0.8.0``: ``ILmControl`` replaces ``ControlClient``. The top-level
  ``fallback_run_target`` is mandatory, ``number_of_attempts`` is limited to
  ``255``, and ``application_type: Reporting`` only allows the ready condition
  ``Running``
  (`Lifecycle v0.8.0 release notes <https://github.com/eclipse-score/lifecycle/releases/tag/v0.8.0>`__).
- ``v0.9.0``: ``deployment_config.ready_recovery_action`` is deprecated and
  will be removed with the next release
  (`Lifecycle v0.9.0 release notes <https://github.com/eclipse-score/lifecycle/releases/tag/v0.9.0>`__).
- ``v0.10.0``: the configuration ``schema_version`` is ``2``; POSIX RLIMITs
  replace the options ``max_memory_usage`` and ``max_cpu_usage``
  (`lifecycle#868 <https://github.com/eclipse-score/lifecycle/pull/868>`__,
  `Lifecycle v0.10.0 release notes <https://github.com/eclipse-score/lifecycle/releases/tag/v0.10.0>`__).

.. note::

   Important for integrators: the Launch Manager configuration of the
   ``simple_lifecycle`` showcase in ``reference_integration`` uses the new
   schema and can serve as an example
   (`a575ce6 <https://github.com/eclipse-score/reference_integration/commit/a575ce6982f0d73ed759462f25f29d2d39ab7627>`__,
   `9c0136e <https://github.com/eclipse-score/reference_integration/commit/9c0136e094cfd76219077877a760c0e6fb8236d6>`__).

Action required: rename the duration fields to ``*_ms`` and convert the values
to milliseconds, migrate State Managers from ``ControlClient`` to
``ILmControl``, set ``schema_version`` to ``2``, replace
``ready_recovery_action.restart`` with ``activation_retry_attempts`` and
``delay_before_restart_ms``, and replace ``max_memory_usage`` with
``RLIMIT_AS``, ``RLIMIT_STACK`` or ``RLIMIT_DATA`` and ``max_cpu_usage`` with
``RLIMIT_CPU``.

Tooling: safety analysis and dependable element rules
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tooling ``v2.3.1`` and ``v3.0.0`` change the Bazel rules that modules use for
their safety documentation: ``fmea`` became ``safety_analysis``, which
``v3.0.0`` splits into ``failure_modes``, ``fault_trees`` and
``safety_analysis``; ``dependable_element`` no longer has the attribute
``assumptions_of_use``; PlantUML elements are identified by their written name
instead of the alias; the crate repository is renamed from ``@crates`` to
``@crates_score_tooling``
(`Tooling v2.3.1 release notes <https://github.com/eclipse-score/tooling/releases/tag/v2.3.1>`__,
`Tooling v3.0.0 release notes <https://github.com/eclipse-score/tooling/releases/tag/v3.0.0>`__).

.. note::

   Important for integrators: Logging ``v0.2.6`` and Configuration Management
   ``v0.3.1`` still set ``assumptions_of_use``; ``reference_integration``
   removes the attribute by patch
   (``004-drop-dependable-element-aou-attr.patch`` and
   ``003-drop-dependable-element-aou-attr.patch``)
   (`dc41763 <https://github.com/eclipse-score/reference_integration/commit/dc41763ef74338f1b394adcbcd798f76b85cde35>`__).

Action required: migrate ``dependable_element`` and safety analysis targets
with the migration checklist of the Tooling ``v3.0.0`` release notes.

Test Scenarios: libraries moved under ``score/``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Test Scenarios ``v0.5.0`` moved the libraries to
``@score_test_scenarios//score/test_scenarios_cpp`` and
``@score_test_scenarios//score/test_scenarios_rust``
(`testing_tools#31 <https://github.com/eclipse-score/testing_tools/pull/31>`__).

.. note::

   Important for integrators: the feature integration tests of
   ``reference_integration`` use the new labels
   (`cb89c10 <https://github.com/eclipse-score/reference_integration/commit/cb89c10a49e1058ca6e4f01495530be30db5441b>`__).

Action required: update the ``@score_test_scenarios`` labels.

Docs-as-code: ``score_pytest`` moved, FMEA attribute renamed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Docs-as-code ``v8.4.0`` removed the ``score_pytest`` macro and the test
attributes plugin; they are provided by ``score_tools``. The attribute
``root_cause`` of ``feat_fmea`` and ``comp_fmea`` was renamed to
``failure_root_cause``
(`Docs-as-code v8.4.0 release notes <https://github.com/eclipse-score/docs-as-code/releases/tag/v8.4.0>`__).

Action required: load ``score_pytest`` from ``@score_tools`` and rename
``root_cause`` in FMEA needs.

🎯 Reference Integration scope
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- **Version:** ``v0.10.0``
- **Source / tag:** `Reference integration <https://github.com/eclipse-score/reference_integration/tree/v0.10.0>`__
- **Release notes:** `Reference integration release notes <https://github.com/eclipse-score/reference_integration/releases/tag/v0.10.0>`__
- **Platform Verification Report:** :need:`doc__platform_verification_report_latest`

The *Release notes* column of the module tables links every release of a module
since v0.9.0, oldest first; modules unchanged since v0.9.0 show their current
release.


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
     - `v0.7.3 <https://github.com/eclipse-score/score/releases/tag/v0.7.3>`__ · `v0.7.4 <https://github.com/eclipse-score/score/releases/tag/v0.7.4>`__
     - ---
   * - `Baselibs <https://github.com/eclipse-score/baselibs/tree/v0.2.17>`__
     - ``v0.2.17``
     - `v0.2.13 <https://github.com/eclipse-score/baselibs/releases/tag/v0.2.13>`__ · `v0.2.14 <https://github.com/eclipse-score/baselibs/releases/tag/v0.2.14>`__ · `v0.2.15 <https://github.com/eclipse-score/baselibs/releases/tag/v0.2.15>`__ · `v0.2.16 <https://github.com/eclipse-score/baselibs/releases/tag/v0.2.16>`__ · `v0.2.17 <https://github.com/eclipse-score/baselibs/releases/tag/v0.2.17>`__
     - :doc:`Verification report </modules/score_baselibs/verification_report/module_verification_report>`
   * - `Communication <https://github.com/eclipse-score/communication/tree/v0.6.0>`__
     - ``v0.6.0``
     - `v0.5.0 <https://github.com/eclipse-score/communication/releases/tag/v0.5.0>`__ · `v0.6.0 <https://github.com/eclipse-score/communication/releases/tag/v0.6.0>`__
     - Dependable elements:

       * `LoLa (mw::com) <https://eclipse-score.github.io/communication/v0.6.0/docs/sphinx/mw_com_index/index.html>`__
       * `Message Passing <https://eclipse-score.github.io/communication/v0.6.0/docs/sphinx/dependable_element_message_passing_index/index.html>`__
       * `Shared Memory <https://eclipse-score.github.io/communication/v0.6.0/docs/sphinx/dependable_element_memory_shared_index/index.html>`__
   * - `Persistency <https://github.com/eclipse-score/persistency/tree/v0.4.0>`__
     - ``v0.4.0``
     - `v0.4.0 <https://github.com/eclipse-score/persistency/releases/tag/v0.4.0>`__
     - :doc:`Verification report </modules/score_persistency/verification_report/module_verification_report>`
   * - `Kyron <https://github.com/eclipse-score/kyron/tree/v0.1.6>`__
     - ``v0.1.6``
     - `v0.1.5 <https://github.com/eclipse-score/kyron/releases/tag/v0.1.5>`__ · `v0.1.6 <https://github.com/eclipse-score/kyron/releases/tag/v0.1.6>`__
     - ---
   * - `Lifecycle <https://github.com/eclipse-score/lifecycle/tree/v0.10.0>`__
     - ``v0.10.0``
     - `v0.7.0 <https://github.com/eclipse-score/lifecycle/releases/tag/v0.7.0>`__ · `v0.8.0 <https://github.com/eclipse-score/lifecycle/releases/tag/v0.8.0>`__ · `v0.9.0 <https://github.com/eclipse-score/lifecycle/releases/tag/v0.9.0>`__ · `v0.10.0 <https://github.com/eclipse-score/lifecycle/releases/tag/v0.10.0>`__
     - :doc:`Verification report </modules/score_lifecycle/verification_report/module_verification_report>`
   * - `Logging <https://github.com/eclipse-score/logging/tree/v0.2.6>`__
     - ``v0.2.6``
     - `v0.2.5 <https://github.com/eclipse-score/logging/releases/tag/v0.2.5>`__ · `v0.2.6 <https://github.com/eclipse-score/logging/releases/tag/v0.2.6>`__
     - :doc:`Verification report </modules/score_logging/verification_report/module_verification_report>`
   * - `Time <https://github.com/eclipse-score/time/tree/v0.3.1>`__
     - ``v0.3.1``
     - `v0.3.0 <https://github.com/eclipse-score/time/releases/tag/v0.3.0>`__ · `v0.3.1 <https://github.com/eclipse-score/time/releases/tag/v0.3.1>`__
     - ---
   * - `Configuration Management <https://github.com/eclipse-score/config_management/tree/v0.3.1>`__
     - ``v0.3.1``
     - `v0.3.1 <https://github.com/eclipse-score/config_management/releases/tag/v0.3.1>`__
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
     - `v0.0.11 <https://github.com/eclipse-score/score-crates/releases/tag/v0.0.11>`__
   * - `ITF (Integration Testing Framework) <https://github.com/eclipse-score/itf/tree/v0.6.0>`__
     - ``v0.6.0``
     - `v0.6.0 <https://github.com/eclipse-score/itf/releases/tag/v0.6.0>`__
   * - `Devcontainer <https://github.com/eclipse-score/devcontainer/tree/v1.11.4>`__
     - ``v1.11.4``
     - `v1.11.4 <https://github.com/eclipse-score/devcontainer/releases/tag/v1.11.4>`__
   * - `Tools <https://github.com/eclipse-score/tools/tree/v0.0.4>`__
     - ``v0.0.4``
     - `v0.0.4 <https://github.com/eclipse-score/tools/releases/tag/v0.0.4>`__
   * - `Tooling <https://github.com/eclipse-score/tooling/tree/v3.0.1>`__
     - ``v3.0.1``
     - `v2.1.0 <https://github.com/eclipse-score/tooling/releases/tag/v2.1.0>`__ · `v2.1.1 <https://github.com/eclipse-score/tooling/releases/tag/v2.1.1>`__ · `v2.2.0 <https://github.com/eclipse-score/tooling/releases/tag/v2.2.0>`__ · `v2.2.1 <https://github.com/eclipse-score/tooling/releases/tag/v2.2.1>`__ · `v2.2.2 <https://github.com/eclipse-score/tooling/releases/tag/v2.2.2>`__ · `v2.2.3 <https://github.com/eclipse-score/tooling/releases/tag/v2.2.3>`__ · `v2.3.0 <https://github.com/eclipse-score/tooling/releases/tag/v2.3.0>`__ · `v2.3.1 <https://github.com/eclipse-score/tooling/releases/tag/v2.3.1>`__ · `v3.0.0 <https://github.com/eclipse-score/tooling/releases/tag/v3.0.0>`__ · `v3.0.1 <https://github.com/eclipse-score/tooling/releases/tag/v3.0.1>`__
   * - `Bazel Platforms <https://github.com/eclipse-score/bazel_platforms/tree/v1.1.0>`__
     - ``v1.1.0``
     - `v1.1.0 <https://github.com/eclipse-score/bazel_platforms/releases/tag/v1.1.0>`__
   * - `Test Scenarios <https://github.com/eclipse-score/testing_tools/tree/v0.5.0>`__
     - ``v0.5.0``
     - `v0.5.0 <https://github.com/eclipse-score/testing_tools/releases/tag/v0.5.0>`__
   * - `Docs-as-code <https://github.com/eclipse-score/docs-as-code/tree/v8.6.0>`__
     - ``v8.6.0``
     - `v8.1.2 <https://github.com/eclipse-score/docs-as-code/releases/tag/v8.1.2>`__ · `v8.2.0 <https://github.com/eclipse-score/docs-as-code/releases/tag/v8.2.0>`__ · `v8.3.0 <https://github.com/eclipse-score/docs-as-code/releases/tag/v8.3.0>`__ · `v8.4.0 <https://github.com/eclipse-score/docs-as-code/releases/tag/v8.4.0>`__ · `v8.5.0 <https://github.com/eclipse-score/docs-as-code/releases/tag/v8.5.0>`__ · `v8.5.1 <https://github.com/eclipse-score/docs-as-code/releases/tag/v8.5.1>`__ · `v8.6.0 <https://github.com/eclipse-score/docs-as-code/releases/tag/v8.6.0>`__
   * - `Process description <https://github.com/eclipse-score/process_description/tree/v2.2.2>`__
     - ``v2.2.2``
     - `v2.2.0 <https://github.com/eclipse-score/process_description/releases/tag/v2.2.0>`__ · `v2.2.1 <https://github.com/eclipse-score/process_description/releases/tag/v2.2.1>`__ · `v2.2.2 <https://github.com/eclipse-score/process_description/releases/tag/v2.2.2>`__
   * - `Bazel CPP Toolchain <https://github.com/eclipse-score/bazel_cpp_toolchains/tree/v1.0.3>`__
     - ``v1.0.3``
     - `v1.0.3 <https://github.com/eclipse-score/bazel_cpp_toolchains/releases/tag/v1.0.3>`__

💿 Images
----------

.. list-table::
   :header-rows: 1
   :widths: 30 15 15 40

   * - Name
     - Download
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
     - `eclipse-autosd-bootc-qemu-x86_64.qcow2.xz <https://github.com/eclipse-score/reference_integration/releases/download/v0.10.0/eclipse-autosd-bootc-qemu-x86_64.qcow2.xz>`__
     - `How-to <https://github.com/eclipse-score/reference_integration/blob/v0.10.0/README.md#operating-system-integrations>`__
     - Red Hat AutoSD x86_64 QEMU image (qcow2) with the S-CORE showcases.
   * - Reference Elektrobit corbos Linux for Safety Applications image (Experimental)
     - ---
     - `How-to <https://github.com/eclipse-score/reference_integration/blob/v0.10.0/images/ebclfsa_aarch64/README.md>`__
     - Elektrobit corbos Linux for Safety Applications (aarch64) image.

🐞 Known Issues/Vulnerabilities and Bug Fixes
----------------------------------------------

- See the release notes of the individual modules.
- Safety Package(s) not completed for modules and platform. To qualify the S-CORE platform these gaps must be filled.

🚀 Upgrade Instructions
------------------------

- Increase to the newest Bazel registry versions: https://eclipse-score.github.io/bazel_registry_ui
- The module versions of this release are listed in `known_good.json <https://github.com/eclipse-score/reference_integration/blob/v0.10.0/known_good.json>`__.


📧 Contact Information
-----------------------

For any questions or support, please contact the *Project leads* or raise an issue/discussion.
https://projects.eclipse.org/projects/automotive.score

