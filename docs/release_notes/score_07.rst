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

S-CORE v0.7-release notes
=========================

.. document:: S-CORE v0.7 release note
   :id: doc__score_v07_release_note
   :status: draft
   :safety: QM
   :security: YES
   :realizes: wp__platform_sw_release_note

| **Platform Release:** S-CORE
| **Release Tag:** v0.7.0
| **Origin Release Tag**: v0.6
| **Release Date:** 2026-05-11


Overview
^^^^^^^^

The SCORE 0.7 platform release centers on safety formalization (vulnerability management, OS tier definitions, safety manuals), Rust interoperability (FFI bindings in baselibs and a full Rust COM API in communication),
and infrastructure hardening (toolchain improvements, Dependabot, CodeQL).

The release significantly expanded integration testing capabilities, with ITF upgrade and test execution now supported on both Docker and QNX targets using the new py_itf_test Bazel rule. 
The CI/CD pipeline was overhauled — the bash-based integration script was replaced with Python and the pipeline became more robust with improved build caching, automatic cancellation of superseded runs, and workflow steps pinned to exact commit SHAs for supply-chain safety. 
EBcLfSA integration was updated to the new structure and extended with Rust application support.
On the documentation side, the build pipeline was fixed and an integration status dashboard was introduced to provide visibility into module health across the platform. 
Infrastructure-wise, Bzlmod lockfile consistency is now enforced in CI, the AutoSD image version is frozen for reproducible builds, and image filesystem rules were migrated to the new Bazel API.

Eclipse S-CORE book
-------------------
The `Eclipse S-CORE book <https://eclipse-score.github.io/score/main/handbook/index.html>`_
is a “how-to” guide for users getting started with the project or who want to contribute new modules.

S-CORE Platform
^^^^^^^^^^^^^^^^^^

- **Version:** ``score v0.5.5``
- **Release notes**: `S-CORE Platform release notes <https://github.com/eclipse-score/score/releases/tag/v0.5.5>`_



Integrated Software Modules
-----------------------------

Baselibs
~~~~~~~~~~~~~
Selection of basic C++ utility libraries for common use in the S-CORE project

- **Version:** ``baselibs v0.2.7``
- **Release notes**: `Baselibs release notes <https://github.com/eclipse-score/baselibs/releases/tag/v0.2.7>`_

Baselibs Rust
~~~~~~~~~~~~~

Selection of basic Rust utility libraries for common use in the S-CORE project

- **Version:** ``baselibs_rust v0.1.2``
- **Release notes**: `Baselibs Rust release notes <https://github.com/eclipse-score/baselibs_rust/releases/tag/v0.1.2>`_


Communication
~~~~~~~~~~~~~
Zero-copy, shared-memory based inter-process communication for minimal-latency intra-ECU messaging.

- **Version:** ``communication v0.2.1``
- **Release notes**: `Communication release notes <https://github.com/eclipse-score/communication/releases/tag/v0.2.1>`_


Persistency
~~~~~~~~~~~
Ensures long-term storage and retrieval of data and provides a reliable mechanism for
preserving application state and data integrity over time.

- **Version:** ``persistency v0.3.2``
- **Release notes**: `Persistency release notes <https://github.com/eclipse-score/persistency/releases/tag/v0.3.2>`_


Logging
~~~~~~~

- **Version:** ``logging v0.2.1``
- **Release notes**: `Logging release notes <https://github.com/eclipse-score/logging/releases/tag/v0.2.1>`_


Orchestrator
~~~~~~~~~~~~~
Orchestrator module provides a framework for defining and executing complex workflows and task sequences in a coordinated manner.

- **Version:** ``orchestrator v0.1.1``
- **Release notes**: `Orchestrator release notes <https://github.com/eclipse-score/orchestrator/releases/tag/v0.1.1>`_


Kyron
~~~~~~~~~~~~~~
Kyron is a customizable, high-performance async/await runtime designed for advanced concurrent programming with focus on functional safety.
It allows fine-grained control over scheduling, thread management, and workload isolation through configurable execution engines.

- **Version:** ``kyron v0.1.2``
- **Release notes**: `Kyron release notes <https://github.com/eclipse-score/kyron/releases/tag/v0.1.2>`_


Lifecycle & Health Management
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Lifecycle module provides a Launch Manager for process lifecycle management as well as a Health Monitoring library to support supervision of process behavior.

- **Version:** ``lifecycle v0.2.0``
- **Release notes**: `Lifecycle release notes <https://github.com/eclipse-score/lifecycle/releases/tag/v0.2.0>`_


Reference integration
~~~~~~~~~~~~~~~~~~~~~~
Central integration of Eclipse S-CORE modules

- **Version:** ``reference integration v0.7.0``
- **Source / tag:** `Reference Integration GitHub release <https://github.com/eclipse-score/reference_integration/releases/tag/v0.7.0>`_


Reference QNX image
+++++++++++++++++++++
- No changes compared to the previous software version.

Reference Red Hat AutoSD Linux image (Experimental)
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

- No changes compared to the previous software version.


Reference Elektrobit corbos Linux for Safety Applications Linux image (Experimental)
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

- No changes compared to the previous software version.

Associated Infrastructure Modules
-----------------------------------

process_description
~~~~~~~~~~~~~~~~~~~
Provides a process model establishing organizational rules for developing open source software
in the automotive domain, suitable for safety and security contexts.

- **Version:** ``process description v1.5.4``
- **Release notes**: `process_description release <https://github.com/eclipse-score/process_description/releases/tag/v1.5.4>`_

docs-as-code
~~~~~~~~~~~~~~
Tooling for linking and generation of documentation.

- **Version:** ``docs-as-code v4.0.3``
- **Source / tag:** `docs-as-code GitHub release <https://github.com/eclipse-score/docs-as-code/releases/tag/v4.0.3>`_

tooling
~~~~~~~~~~~~~~
Tooling for S-CORE development.

- **Version:** ``tooling v1.1.2``
- **Source / tag:** `tooling GitHub release <https://github.com/eclipse-score/tooling/releases/tag/v1.1.2>`_


ITF (Integration Testing Framework)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
ITF is a pytest-based testing framework designed for ECU (Electronic Control Unit) testing in automotive domains. 
It provides a flexible, plugin-based architecture that enables testing on multiple target environments including Docker containers,
QEMU virtual machines, and real hardware.

- **Version:** ``itf v0.3.0``
- **Source / tag:** `ITF GitHub release <https://github.com/eclipse-score/itf/releases/tag/v0.3.0>`_

Test Scenarios
~~~~~~~~~~~~~~~
Test scenarios provide a backend for defining C++ and Rust implemented test scenarios that allow parametrized execution of built scenario applications which are the input for test cases.

- **Version:** ``Test Scenarios v0.4.1``
- **Source / tag:** `Test Scenarios GitHub release <https://github.com/eclipse-score/testing_tools/releases/tag/v0.4.1>`_


Bazel CPP Toolchain
~~~~~~~~~~~~~~~~~~~~
- **Version:** ``bazel_cpp_toolchains v0.5.1``
- **Release notes**: `Bazel CPP Toolchain release notes <https://github.com/eclipse-score/bazel_cpp_toolchains/releases/tag/v0.5.1>`_


Known Issues
----------------------
- see release notes of every module separately

Upgrade Instructions
----------------------
- Increase to newest bazel registry versions: https://eclipse-score.github.io/bazel_registry_ui
- Versions can be found under: https://github.com/eclipse-score/reference_integration/blob/v0.7.0/known_good.json

Contact Information
----------------------
For any questions or support, please contact the *Project leads* or raise an issue/discussion.
https://projects.eclipse.org/projects/automotive.score
