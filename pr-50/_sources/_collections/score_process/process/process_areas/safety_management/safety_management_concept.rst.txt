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

.. doc_concept:: Safety Management Concept
   :id: doc_concept__safety_management_process
   :status: valid

In this section a concept for the Safety Management will be discussed.
Inputs for this concepts are mainly the requirements of ISO26262 "Part 2: Management of functional safety".

Key concept
^^^^^^^^^^^
The Safety Management Plan establishes a comprehensive strategy for managing all identified safety activities throughout the entire project life cycle.
It ensures that these activities are executed in a systematic, effective, and repeatable manner, providing clear guidance on responsibilities, processes, and control measures.
This approach supports risk mitigation, regulatory compliance, and continuous improvement, enabling the project team to maintain safety standards consistently from initiation to completion.

Inputs
^^^^^^

#. Stakeholders for the Safety Management work products?
#. Which safety plans do we have?
#. Which other work products of Safety Management are important?
#. What tooling do we need?

Stakeholders
^^^^^^^^^^^^

#. :need:`Safety Manager <rl__safety_manager>`

   * Main responsible to ensure ISO 26262 compliance in the project
   * Create/Maintain Safety Plan
   * Approve Component Classification
   * Approve Safety Package
   * Approve Safety Audit
   * Approve Formal Reviews
   * Approve Safety Manual
   * Monitor/Verify Safety
   * Impact Analysis of Change Request
   * Status reporting of safety activities

#. :need:`Safety Engineer <rl__safety_engineer>`

   * Supporting the Safety Manager
   * Create/Maintain Safety Package
   * Create/Maintain Safety Manual

#. :need:`Project Lead <rl__project_lead>`

   * Planning of development for platform projects
   * Approve Safety Plan
   * Approve Safety Release Notes
   * Approve Impact Analysis of Change Request

#. :need:`Committer <rl__committer>`

   * Planning of development for module projects (as a Module Project Lead)
   * Performing safety related development
   * Create Component Classification

#. :need:`External Auditor <rl__external_auditor>`

   * Perform Safety Audit as independent safety audits
   * Perform Formal Reviews (e.g., safety plans, safety packages, safety analyses).
   * Verifies compliance with defined safety processes and standards.
   * Reports audit results and decides on pass/fail status.

Safety Plans
^^^^^^^^^^^^

The SW platform project defines two levels of planning: platform and module. There will be one safety plan on platform level and several safety plans on module level (one for each module).
This safety planning follows how development teams and repositories are organized in the project. Each of these safety plans "creates" one SEooC.
The :need:`Platform Safety Plan <wp__platform_safety_plan>` exists only once and is part of the :need:`Platform Management Plan <wp__platform_mgmt>`.

Safety Management Work Products
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Apart from the safety plans the main work products of Safety Management are:

* :need:`Safety Manual <wp__platform_safety_manual>` - the safety manual defines the requirements for safe usage or integration of the SW platform (or its individual modules)
* :need:`Formal Document Review Reports <wp__fdr_reports>` - on safety plan, safety package and safety analyses, according to ISO 26262 requirements
* :need:`Safety Package <wp__platform_safety_package>` - the safety package contains the released work products planned in the safety plan, it does not contain the safety argumentation. By this the project ensures it does not take over liability for the SW platform (or its individual modules). But it enables the user to integrate the SW platform (or its individual modules) in their safety case.

Safety Management Tooling
^^^^^^^^^^^^^^^^^^^^^^^^^

For the safety planning and safety manual a “Docs-as-Code” approach is used and within that approach Id will be used for referencing.

For the activities planning (who, when) we use a Issue Tracking System to create and manage issues, and monitor progress through a project management dashboard.

For the reporting (e.g. displaying the status of the work products) additional tooling is created.
