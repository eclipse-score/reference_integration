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


Guideline
#########

.. gd_guidl:: Process Management Guideline
   :id: gd_guidl__process_management
   :status: valid
   :tags: process_management
   :complies: std_req__iso26262__management_5421, std_req__iso26262__management_5422, std_req__aspice_40__gp-311

This document describes the general guidances for Process Management based on the concept which is defined :need:`[[title]]<doc_concept__process_management>`.

General Hints
=============

The detailed implementation of all process areas defined in the process description for
the project shall be described in the
:ref:`Workflow Platform Management <workflow_platform_management>`.

Templates
---------

The process and strategy description shall use the following templates:
:ref:`process_management_templates`.

Requirements
------------

For the process descriptions the following mandatory requirements exist:

.. needtable:: Overview of mandatory process description requirements
   :tags: process_management
   :filter: "mandatory" in tags and "attribute" in tags and "process_management" in tags and is_external == False
   :style: table
   :columns: title
   :colwidths: 30


.. _workflow_process_management_requirements:


Activities for Process Management
=================================

This section describes in detail which steps need to be performed for the process
Management.

.. list-table:: Activities for Process Management
   :header-rows: 1
   :widths: 10,60,30,30

   * - Step
     - Description
     - Responsible
     - Approver
   * - :ref:`1. <pm_create_maintain_strategy>`
     - Create/Maintain Process Management Strategy
     - :need:`[[title]] <rl__contributor>`
     - :need:`[[title]] <rl__process_community>`
   * - :ref:`2. <pm_define_approve_process_description>`
     - Define/Approve Process Description
     - :need:`[[title]] <rl__contributor>`
     - :need:`[[title]] <rl__process_community>`
   * - :ref:`3. <pm_monitor_improve_process>`
     - Monitor/Control Process Implementation
     - :need:`[[title]] <rl__contributor>`
     - :need:`[[title]] <rl__process_community>`


.. _pm_create_maintain_strategy:

Create/Maintain Process Strategy
--------------------------------

:need:`[[title]] <rl__contributor>` (as author, submitter) creates and maintains the
process management strategy. They create Pull request (PR) for contributions.

The potential contribution is discussed during the public Process Community Meetings
or standard pull request reviews and if decided to implement,
:need:`[[title]] <rl__process_community>` approves the Pull Request to include
the contribution in the process strategy.


.. _pm_define_approve_process_description:

Define/Approve Process Description
----------------------------------

:need:`[[title]] <rl__contributor>` (as author, submitter) creates and maintains the
process description. They create Pull request (PR) for contributions.

The potential contribution is discussed during the public Process Community Meetings
or standard pull request reviews and if decided to implement,
:need:`[[title]] <rl__process_community>` approves the Pull Request to include
the contribution in the process description.

.. _pm_monitor_improve_process:

Monitor/Improve Process
-----------------------

If potential improvements are detected, the :need:`[[title]] <rl__contributor>` triggers
an ISSUE for improvement by using the
`Issue Template Improvement <https://github.com/eclipse-score/process_description/blob/main/.github/ISSUE_TEMPLATE/2-improvement.yml>`_.

The potential improvement is discussed during the public Process Community Meetings
and if decided to implement, a pull request to follow :ref:`pm_create_maintain_strategy`
or :ref:`pm_define_approve_process_description` must be created.
