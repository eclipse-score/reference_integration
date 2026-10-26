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

score_config_management
========================

Step 5 — Component-test plan
-----------------------------

.. note::

   The Reference Integration does not yet have a component-test stage (see
   :doc:`../integration_process/step_5_component_tests`). This page documents the
   plan for ``score_config_management`` so the module is ready to be wired in as
   soon as the mechanism exists.

Scope
~~~~~

The plan covers the **config_daemon** component only. ``config_provider`` is a
client-side library with no standalone runnable binary today; it is out of scope
until a dedicated test harness exists for it.

Component under test
~~~~~~~~~~~~~~~~~~~~~

``config_daemon`` — the service that owns and exposes parameter-set data over its
public ``mw::com`` service interface
(``score/config_management/config_daemon/code/services/internal_config_provider_service.h``),
consumed by ``config_provider`` clients.

Reference application
~~~~~~~~~~~~~~~~~~~~~~

Reuse the ``config_daemon`` binary and configuration already packaged for the
Step 4 showcase (``showcases/standalone/config_management.score.json`` /
``@score_config_management//score/config_management/config_daemon/code:config_daemon``).
No new binary needs to be built for the component test; it drives the same
reference application already validated to run.

Planned test approach
~~~~~~~~~~~~~~~~~~~~~~

Once the component-test framework is introduced:

#. Start the reference ``config_daemon`` application with its existing showcase
   configuration (``etc/mw_com_config.json``).
#. Drive it as a black box through its public ``InternalConfigProvider``
   ``mw::com`` service interface only — no internal/implementation-detail access.
#. Assert parameter-set retrieval behavior (successful reads, missing/invalid
   parameter handling, service availability) against the component's documented
   interface specification.
#. Run independently of other modules and of full integration images, per the
   Step 5 definition of component-level verification.

Status
~~~~~~

Documented plan only — **not yet executable**. No component-test stage exists in
the Reference Integration CI yet; this page will be updated with the actual
wiring once Step 5 tooling lands.
