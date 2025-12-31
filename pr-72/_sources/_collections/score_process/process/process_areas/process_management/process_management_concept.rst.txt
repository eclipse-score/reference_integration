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
###################

.. doc_concept:: Concept Description
   :id: doc_concept__process_management
   :status: valid
   :tags: process_management

In this section concepts for the Process Management are discussed. Inputs for these
concepts are the requirements of ISO26262 Part-2, ISO/SAE21434 Clause 5 and ASPICE
Requirements from PA 3.1 Process definition process attribute, additionally including
the requirements of the different stakeholders for the Process Management process.

Key concept
***********
A suitable standard process for developing software in an Open-Source environment is
developed. The standard process aka process description is based on building blocks
as shown here: :ref:`processes_introduction`.
The central building blocks is the 'workflow' representing activities.
Workflows have inputs and outputs, roles executing them and guidances to support the
execution.
Especially process requirements are defined to support automatic checks from tools
designed for process deployment and implementation.
Finally workflows are linked to standard requirements to show compliance with them.

Inputs
******

#. Stakeholders for the Process Management?
#. Which building blocks are required?
#. Which activities are required?

Stakeholders for the Process Management
***************************************

#. :need:`Contributor <rl__contributor>`

   * Contributes workflows, work products, guidances to grow the process content
   * Creates, Maintains Strategy
   * Defines, Monitors, Improves Strategy, Process Description and Implementation

#. :need:`Process Community <rl__process_community>`

   * Verifies that the contribution including strategy and definitions fulfills the project policies
   * Approves contributions

#. :need:`Project Lead <rl__project_lead>`

   * Supports all activities

#. :need:`External Auditor <rl__external_auditor>`

   * Supports all activities, especially during iterative audits

Standard Requirements
=====================

Also requirements of standards need to be taken into consideration:

* ISO 26262
* ASPICE
* ISO SAE 21434


.. _pm_building_blocks:

Building blocks
***************

The required building blocks for the process description are defined here:
:ref:`process_management_templates`.
They are complemented by requirements here: :ref:`process_management_requirements`.

Activities for process management
*********************************

In general strategy, process descriptions and improvements are discussed during
public Process Community Meetings. The Meeting schedules are available in the public
calendar here: <https://calendar.google.com/calendar/u/0/r/month>.
So every :need:`rl__contributor` can join them discuss topics from interest there.

.. _pm_cm_strategy:

Creation/Maintenance of the Process Management Strategy
=======================================================
The process management strategy is part of the :ref:`process_description`.

The process (meta) model (see :ref:`processes_introduction`) summarizes the strategy.

Further strategical concepts are defined here: :ref:`process_general_concepts`.

Every :need:`rl__contributor` can join the community meetings and contribute
using standard pull requests.

Strategy changes are approved by the :need:`rl__process_community`.

.. _pm_da_process:

Definition/Approval of the Process Description
==============================================
The process description is defined here: :ref:`process_description`.

:ref:`process_areas` as part of that representing the process definitions.

Every :need:`rl__contributor` can join the community meetings and contribute
using standard pull requests.

Process Description are approved by the :need:`rl__process_community`.

Regular audits supported by :need:`rl__external_auditor` ensure compliance with
existing standards.

.. _pm_mc_process:

Monitoring/Improving of the Process Description Implementation
==============================================================
The process strategy and description implementation is monitored and improvements are
triggered, if required.

Every :need:`rl__contributor` can propose improvements using the project ISSUE Tracking
system.

Improvements are approved by the :need:`rl__process_community`.
