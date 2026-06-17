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

###################
Integration Process
###################

This document is a step-by-step *how-to* for module owners who want to integrate
their own S-CORE module into the **Reference Integration** for the first time.

It walks you through everything from registering the module in
``known_good.json`` over wiring it into the Bazel build, the showcases, the
images and the CLI, up to adding it to the CI/CD pipelines and the consolidated
reporting (documentation, coverage and verification reports).


What "integration" means here
=============================

The Reference Integration is a single `Bazel (bzlmod) <https://bazel.build/external/overview#bzlmod>`_
build that pulls every S-CORE module together at a defined commit, builds them
against each other and runs their tests, showcases and reports.

Integrating a module is **incremental**: each step below builds on the previous
one and *extends the reach* of your module a little further into the
integration. You climb the ladder only as far as your module needs — a pure
library may stop after it builds in-tree, while a module with a runnable example
goes all the way to running on every target platform and being exercised by
integration tests.

The chapters that follow walk this ladder in order. Stop at whatever rung makes
sense for your module.


Prerequisites
=============

Before you start, make sure that:

* Your module lives in its own GitHub repository under the ``eclipse-score``
  organization and is a **bzlmod module**, i.e. it has a top-level
  ``MODULE.bazel`` with a ``module(name = "score_<your_module>")`` declaration.
* The module name follows the ``score_<name>`` convention (e.g.
  ``score_communication``). The same name is used as the Bazel
  ``bazel_dep`` / repository name (``@score_<name>//...``).
* The module builds and tests pass standalone on Linux ``x86_64``.
* You know the commit hash you want to pin (the integration always pins an exact
  commit, never a floating branch).


The integration steps
======================

Work through the chapters in order — each one extends the reach of your module a
little further into the integration:

.. toctree::
   :maxdepth: 2
   :numbered:

   step_1_add_module
   step_2_documentation
   step_3_unit_tests
   step_4_platforms
   step_5_component_tests
   step_6_integration_tests
   step_7_reporting
   step_8_code_quality
   checklist
   reference
