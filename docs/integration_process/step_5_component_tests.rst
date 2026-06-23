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

Step 5 — Add component tests
============================

.. admonition:: What it unlocks
   :class: tip

   **Component-level verification** — Your module is verified **in isolation as
   a component** — its public interfaces are tested against their specification,
   independently of the other modules and of the full integration images.

.. warning::

   **Currently missing — needs to be introduced.** There is no component-test
   stage in the Reference Integration yet. Component tests (testing a single
   module's components/interfaces in isolation, between unit tests in Step 3 and
   the runtime feature integration tests in Step 6) still need to be designed and
   wired into the integration and its CI. This step is a placeholder so the
   intended test pyramid is documented; update it once the mechanism exists.
