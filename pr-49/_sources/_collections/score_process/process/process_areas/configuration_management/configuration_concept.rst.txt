..
   # *******************************************************************************
   # Copyright (c) 2025 Contributors to the Eclipse Foundation
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

Concept Description
-------------------

.. doc_concept:: Configuration Management Concept
   :id: doc_concept__configuration_process
   :status: valid

In this section a concept for the configuration management will be discussed.
Inputs for this concepts are mainly the requirements of ISO26262 "Part 8: Supporting Processes"
and ASPICE Requirements from PAM4.0, SUP.8

Key concept
^^^^^^^^^^^
The Configuration Management Plan should define the strategy to manage the configuration items
in an effective and repeatable way for the project life cycle.

Note: configuration items are all realizations of defined work products in the project plus additional arefacts not developed by the project
needed for the building of the binaries, documentation and verification reports (e.g. tools, external SW libraries).

Inputs
^^^^^^

#. Stakeholders for the configuration process work products?
#. Who needs which information?
#. Which configuration items do we have?
#. What tooling do we need?

Stakeholders
^^^^^^^^^^^^

#. :need:`Project Lead <rl__project_lead>`

   * for creating a module or a platform release a baseline of all configuration items is needed

#. :need:`Contributor <rl__contributor>` and :need:`Committer <rl__committer>`

   * wants know which work products's version has to be used as input for his work
   * wants to share their created work product with others for example to get those reviewed
   * wants to integrate their created work product with other work products

Configuration Management Tooling
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Almost all requirements of the standards towards configuration management can be covered by
standard versioning tooling and of tooling for the "Docs-as-Code" approach.

For the automated storage additional tooling is needed see :doc:`guidance/configuration_process_req`)
