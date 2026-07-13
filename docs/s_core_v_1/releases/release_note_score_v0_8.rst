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

S-CORE Platform v0.8 release note
=================================

.. document:: S-CORE v0.8 release note
   :id: doc__score_v08_release_note
   :status: valid
   :safety: QM
   :security: YES
   :realizes: wp__platform_sw_release_note

| **Platform Release:** S-CORE
| **Release Tag:** v0.8.0
| **Origin Release Tag**: v0.7.0
| **Release Date:** TBD


Overview
^^^^^^^^

This document provides an overview of the changes, improvements, and bug fixes included in the software platform release version v0.8.0 as compared to the previous platform release (v0.7.0).

Release-specific summary content for v0.8 is to be added.

Disclaimer
----------

This release note does not "release for production", as it does not come with a safety argumentation and a performed safety assessment.
The work products compiled in the safety package are created with care according to a process satisfying standards, but the project,
being a non-profit and open source organization, can not take over any liability for its content.

Changes to the Platform
^^^^^^^^^^^^^^^^^^^^^^^

New Features
------------

- Time component integrated into the platform, providing time synchronization and clock services. Repository: `time <https://github.com/eclipse-score/time>`_.

Improvements
------------

Developer Website
~~~~~~~~~~~~~~~~~

The main `S-CORE developer website <https://eclipse-score.github.io/score/main/>`_ was refreshed to provide a clearer entry point with improved navigation and direct access to the most important project information.

User's Guide
~~~~~~~~~~~~

The `User's Guide <https://eclipse-score.github.io/score/main/users_guide/index.html>`_ was updated and now provides a better collection of `key project links <https://eclipse-score.github.io/score/main/users_guide/useful_links.html>`_, complemented by a dedicated `How to get involved <https://eclipse-score.github.io/score/main/contribute/index.html>`_ section for new contributors.

Integration Process Guide
~~~~~~~~~~~~~~~~~~~~~~~~~

A dedicated `Integration Process Guide <https://eclipse-score.github.io/reference_integration/main/integration_process/integration_process.html>`_ was added to the Reference Integration repository to simplify the onboarding and integration of new components into the S-CORE reference integration.

Infra & Tooling Manual
~~~~~~~~~~~~~~~~~~~~~~

The `Infra & Tooling Manual <https://eclipse-score.github.io/infrastructure/dev/index.html>`_ now explains the key infrastructure and tooling concepts and provides practical how-to guidance.

Baselibs Consolidation
~~~~~~~~~~~~~~~~~~~~~~

`Baselibs <https://github.com/eclipse-score/baselibs>`_ and Baselibs Rust were consolidated into a single module and repository, with both now maintained in the Baselibs repository.

Safety Sentinel
~~~~~~~~~~~~~~~

The `Communication module <https://github.com/eclipse-score/communication>`_ introduced the `Safety Sentinel concept <https://github.com/eclipse-score/tooling/tree/main/bazel/rules/rules_score>`_, enabling, among other things, end-to-end traceability checks integrated into the Bazel build system. This is a strong step in the right direction; however, the concept does not yet rely on the tooling agreed across the S-CORE project for requirements, architecture, further S-CORE model item definitions, and traceability checks based on Sphinx and Sphinx-Needs. Harmonization of both approaches is planned for the v0.9 release.

Integration Strategy
~~~~~~~~~~~~~~~~~~~~

A common integration strategy was aligned and documented in `DR-008 <https://eclipse-score.github.io/score/main/design_decisions/DR-008-int.html>`_; its implementation is planned for the v0.9 release.

Roadmap & Overall Status
~~~~~~~~~~~~~~~~~~~~~~~~

A clear `roadmap <https://eclipse-score.github.io/reference_integration/main/s_core_v_1/roadmap/roadmap.html>`_ is now available and broken down into release gates and `project milestones <https://github.com/eclipse-score/score/milestones>`_. The new `Overall Status <https://eclipse-score.github.io/reference_integration/main/s_core_v_1/roadmap/overall_status.html>`_ page summarizes the most important cross-module metrics after each release.

The roadmap and milestones are fully aligned with the goal of delivering the major S-CORE v1.0 release by the end of the year, **providing a stable foundation for further industrialization of the S-CORE platform.**

In a recent S-CORE Technical Lead meeting, it was decided to introduce module qualification levels: ``Release``, ``Experimental``, and ``Preview``. This will make it possible to include all modules in platform releases while giving users clear guidance on each module's maturity and intended usage. The exact definition and rollout concept are planned for the v0.9 release.

S-CORE Platform scope
^^^^^^^^^^^^^^^^^^^^^

- **Version:** ``TBD``
- **Release notes**: TBD

Integrated Software Modules
---------------------------

Baselibs
~~~~~~~~

- **Version:** ``TBD``
- **Release notes**: TBD

Baselibs Rust
~~~~~~~~~~~~~

- **Version:** ``TBD``
- **Release notes**: TBD


Communication
~~~~~~~~~~~~~

- **Version:** ``TBD``
- **Release notes**: TBD


Persistency
~~~~~~~~~~~

- **Version:** ``TBD``
- **Release notes**: TBD


Logging
~~~~~~~

- **Version:** ``TBD``
- **Release notes**: TBD


Time
~~~~

- **Version:** ``v0.0.1``
- **Release notes**: `Time release notes <https://github.com/eclipse-score/time/releases/tag/v0.0.1>`_

- Initial preintegration of the Time module into the S-CORE platform, providing time synchronization and clock services.

Orchestrator
~~~~~~~~~~~~

- **Version:** ``v0.1.1``
- **Release notes**: Scheduled to be archived in v0.9 release.


Kyron
~~~~~

- **Version:** ``v0.1.3``
- **Release notes**: `Kyron release notes <https://github.com/eclipse-score/kyron/releases/tag/v0.1.3>`_


Lifecycle & Health Management
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Version:** ``v0.3.0``
- **Release notes**: `Lifecycle release notes <https://github.com/eclipse-score/lifecycle/releases/tag/v0.3.0>`_


Reference integration
~~~~~~~~~~~~~~~~~~~~~

- **Version:** ``TBD``
- **Source / tag:** TBD

- Added a dedicated `Integration Process Guide <https://eclipse-score.github.io/reference_integration/main/integration_process/integration_process.html>`_ with a step-by-step onboarding path (module onboarding, platform integration, testing, reporting, and code quality checks).
- Introduced the v1.0 roadmap and release-gate documentation in `Roadmap <https://eclipse-score.github.io/reference_integration/main/s_core_v_1/roadmap/roadmap.html>`_, including clearer milestone alignment across process areas.
- Established and continuously refreshed the `Overall Status <https://eclipse-score.github.io/reference_integration/main/s_core_v_1/roadmap/overall_status.html>`_ page to provide release-level visibility on cross-module progress and process-area metrics.


Reference QNX image
+++++++++++++++++++

- Added QNX 8 support for ``aarch64`` including build and configuration artifacts for the reference image.
- Extended QEMU runner support for QNX ``aarch64`` to improve reproducible bring-up and integration testing in CI and local workflows.

Reference Red Hat AutoSD Linux image (Experimental)
+++++++++++++++++++++++++++++++++++++++++++++++++++

- Switched AutoSD image builds to a ``bootc``-based flow, improving image build reproducibility and maintainability.
- Updated related build and CI workflow integration for the new AutoSD image generation approach.


Reference Elektrobit corbos Linux for Safety Applications Linux image (Experimental)
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

- Updated EB corbos image documentation by removing outdated scrample-specific references and aligning the guidance with the current integration setup.
- Refreshed EBcLfSA-specific CI workflow and development-container settings to keep the image pipeline aligned with current tooling.

Associated Infrastructure Modules
---------------------------------

Process description
~~~~~~~~~~~~~~~~~~~

- **Version:** ``TBD``
- **Release notes**: TBD

Docs-as-code
~~~~~~~~~~~~

- **Version:** ``docs-as-code v4.6.1``
- **Source / tag:** `docs-as-code GitHub release <https://github.com/eclipse-score/docs-as-code/releases/tag/v4.6.1>`_

Tooling
~~~~~~~

- **Version:** ``TBD``
- **Source / tag:** TBD


ITF (Integration Testing Framework)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Version:** ``TBD``
- **Source / tag:** TBD

Test Scenarios
~~~~~~~~~~~~~~

- **Version:** ``TBD``
- **Source / tag:** TBD


Bazel CPP Toolchain
~~~~~~~~~~~~~~~~~~~

- **Version:** ``TBD``
- **Release notes**: TBD


Compatibility
^^^^^^^^^^^^^

- **Dependencies:** To be added.

Performed Verification
^^^^^^^^^^^^^^^^^^^^^^

- To be added.

Known Issues/Vulnerabilities and Bug Fixes
------------------------------------------

- To be added.

Upgrade Instructions
--------------------

- To be added.

Upgrade Instructions
^^^^^^^^^^^^^^^^^^^^

To be added.

Contact Information
-------------------

For any questions or support, please contact the *Project leads* or raise an issue/discussion.
https://projects.eclipse.org/projects/automotive.score
