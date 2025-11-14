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

.. gd_guidl:: Problem Resolution Guideline
   :id: gd_guidl__problem_problem
   :status: valid
   :complies: std_req__aspice_40__SUP-9-BP1, std_req__aspice_40__SUP-9-BP5, std_req__aspice_40__SUP-9-BP6, std_req__aspice_40__SUP-9-BP7

This document describes the general guidances for Problem Resolution based on the concept which is defined :need:`[[title]]<doc_concept__problem_process>`.

General Hints
=============

The detailed implementation of the Problem Resolution for the project shall be described in the :ref:`Workflow Platform Management <workflow_platform_management>`.

Templates
---------

To create problem reports, the project shall provide the content of the following template
in project's selected Issue Tracking System: :need:`[[title]]<gd_temp__problem_template>`.

.. note::
  An example template for the Issue Tracking System in GitHub (`GitHub Issues <https://github.com/features/issues>`_)
  can be found here:
  `Issue Template Bugfix <https://github.com/eclipse-score/process_description/blob/main/.github/ISSUE_TEMPLATE/1-bugfix.yml>`_

Attributes
----------

For all Problems following mandatory attributes need to be defined:

.. needtable:: Overview of mandatory problem resolution attributes
   :tags: problem_resolution
   :filter: "mandatory" in tags and "attribute" and "problem_resolution" in tags and is_external == False
   :style: table
   :columns: title
   :colwidths: 30


A more detailed description can be found here: :ref:`prm_process_requirements`

.. _workflow_prm_requirements:

Activities for Problem Resolution
=================================

This section describes in detail which steps need to be performed for a Problem Resolution.

.. list-table:: Activities for Problem Resolution
   :header-rows: 1
   :widths: 10,60,30,30

   * - Step
     - Description
     - Responsible
     - Approver
   * - :ref:`1. <prm_create_problem_report>`
     - Create Problem Report
     - :need:`[[title]] <rl__contributor>`
     - :need:`[[title]] <rl__committer>`
   * - :ref:`2. <prm_analyze_problem_report>`
     - Analyze Problem Report
     - :need:`[[title]] <rl__contributor>`
     - :need:`[[title]] <rl__committer>`
   * - :ref:`3. <prm_initiate_problem_resolution>`
     - Initiate and Monitor Problem Resolution
     - :need:`[[title]] <rl__contributor>`
     - :need:`[[title]] <rl__committer>`
   * - :ref:`4. <prm_monitor_problem_resolution>`
     - Close Problem Resolution
     - :need:`[[title]] <rl__committer>`
     - :need:`[[title]] <rl__technical_lead>`, :need:`[[title]] <rl__module_lead>`

.. _prm_create_problem_report:

Create Problem Report
---------------------

:need:`[[title]] <rl__contributor>` (as author, submitter, reporter) creates the Problem
Report in the defined Issue Tracking System of the project based on the content of the
provided template:
:need:`[[title]]<gd_temp__problem_template>`.

It is expected that the select Issue Tracking system supports template definition. Best
practice is to define a template with the required content, so that it can be copied
from the different users.

.. note::
  For the Issue Tracking System in GitHub, there is a template created, which can be
  be found here:
  `Issue Template Bugfix <https://github.com/eclipse-score/process_description/blob/main/.github/ISSUE_TEMPLATE/1-bugfix.yml>`_

.. note::
  A Problem Report Example based on that template is here:
  `Example Problem Report <https://github.com/eclipse-score/process_description/issues/124>`_

.. note::
  A Problem Report Example 2 based on that template is here:
  `Example Problem Report 2 <https://github.com/eclipse-score/process_description/issues/126>`_

It is expected, that the UID will be provided automatically by the Issue Tracking System.

It is expected, that the status of the problem report is set to "open" automatically.
As long as the content is updated, the status of the Problem is kept "open".

It is expected, that the problem submitter will be set automatically by the Issue
Tracking System.

The title of the Problem Report should reflect the topic accordingly.

The description should reflect the problem root cause and impact in detail.

If applicable affected parties should be notified.

Further supporting information should ge given, especially how to reproduce the problem,
and what is the error occurrence rate?

If the problem affects safety or security it should be stated explicitly.
If safety is affected, the ASIL classification should be added, if applicable.

The problem should be classified according minor, major, critical or blocker.

The affected version of the release should be documented, where the problem was detected.

.. note::
  | For the Problem Report Example:
  | * The UID is provided by the Issue Tracking System as: **#124**
  | * The status of the issue is provided by the Issue Tracking System as: **Open**
  | * The submitter is provided by the Issue Tracking System as: **masc2023**
  | * The title contains the main root cause, missing safety/security attribute
  | * The descriptions has a section for the **Root cause** and **Impact**
  | * The description has a section for notification: **Notification required?**
  | * Further supporting information is added as the link to the official feature request template which makes it reproducible
  | * Checkboxes are selected to highlight, that Safety and Security is affected, no further classification, as the project is defined as ASIL B
  | * The problem classification is provided as minor
  | * The affected version is provided: *pre-0.5*

When ready to review and to analyze, the author sets the status to "in review" manually.

.. note::
  | For the Problem Report Example:
  | * The "Process Development Community" dashboard is added and the status must be changed to **Todo**
  | * The combination of the issue**Open** and **Todo** defines the status **in review**

.. _prm_analyze_problem_report:

Analyze Problem Report
----------------------

The projects :need:`[[title]] <rl__committer>` analyzes the problem together with the
:need:`[[title]] <rl__contributor>` and takes a decision for accepting or rejecting it.

The analysis will start by reviewing all the information given during the creation of the
problem report. All topics are revisited and checked for correctness, completeness and
consistency.

If required, the information is updated accordingly.

If accepted, the stakeholder of the problem and the expected release, where the problem
should be closed, shall be defined. Optionally, the corresponding milestone can be set.

If applicable, the features affected should be identified too.

The description shall reflect the result of the analysis.

.. note::
  | For the Problem Report Example:
  | * The descriptions has a section for the analysis results: **Accepted**
  | * The stakeholder are provided using Assignees field: **masc2023**
  | * The expected closure version is provided: *0.5*
  | * The "Milestone" is provided: **Release 2.0.0 - Maturity Level 2**
  | * Feature identification is not applicable for this example, so no label is set, beside **bug**

If accepted, :need:`[[title]] <rl__contributor>` can start with the initiation of the
Problem Resolution.

The author has the freedom to cancel it at any time by setting the status to "rejected".

.. note::
  | For the Problem Report Example:
  | * For rejection the status of the issue must be changed to **Closed as not planned**
  | * The combination of **Closed as not planned** and any "Process Development Community" status defines the status **rejected**

.. _prm_initiate_problem_resolution:

Initiate and Monitor Problem Resolution
---------------------------------------

If accepted, the projects :need:`[[title]] <rl__committer>` initiates the resolution of
the problem together with the :need:`[[title]] <rl__contributor>`.

The description shall reflect the proposed solutions, e.g. measure to resolve the problem.

.. note::
  | For the Problem Report Example:
  | * The descriptions has a section for the proposed **Solution**

The concrete implementation of the solution may require several additional activities.
In this case additional issues may created and linked to the Problem Report.

.. note::
  | For the Problem Report Example:
  | * The **Create sub-issue** should be used to create further linked issues.

Minimal a Pull Request is sufficient to resolve the problem, which shall be linked
to the Problem Report. It is expected, that the status of the Pull Request is set to
"draft" or "open" automatically.

When ready to implement, the author sets the status to "in implementation" manually.

.. note::
  | For the Problem Report Example:
  | * The "Process Development Community" status must be changed to **In Progress**
  | * The linked Pull Request status is either "Draft" or "Open"
  | * The combination of **Open** and any "Process Development Community" status **In Progress** and the Pull Request status **Draft** or **Open** defines the status **in implementation**

.. note::
  | For the Problem Report Example:
  | * The **Development** section should be used to link to an pull request
  | * The **Create a branch** action may used to create automatically a linked pull request
  | For the Problem Report Example 2:
  | * The **Create a branch** action was used to create a automatically linked Pull Request
  | * The automatically created branch name reflects the issue UID and the title as
  | * **126-bug-stkh_req__archdes_example_req-has-no-content**

During the resolution the responsible lead :need:`[[title]] <rl__technical_lead>` or
:need:`[[title]] <rl__module_lead>` reports regularly the status to the affected
projects teams.

Escalations topics should be documented in the description, if possible.

.. note::
  | For the Problem Report Example and Example 2:
  | * Their is no escalation topic documented

The author has the freedom to cancel it at any time by setting the status to "rejected".

.. _prm_monitor_problem_resolution:

Close Problem Resolution
------------------------

During the resolution the :need:`[[title]] <rl__contributor>` monitors all activities linked to
the problem, until they are closed.

:need:`[[title]] <rl__committer>` checks finally if the problem Resolution is sufficient before
the status is finally closed.
To check, if it is sufficient, :need:`Problem Checklist <gd_chklst__problem_cr_review>` may used.
Further the effectiveness of the implemented measure is confirmed and the availability
of the required reports, as verification results, if applicable.

When confirmed, the author sets the status to "closed" manually, if not done automatically.

.. note::
  | For the Problem Report Example 2:
  | * The status of the issue is provided by the Issue Tracking System as: **Closed**
  | * The combination of **Closed** and any "Process Development Community" status **Done** and the Pull Request status **Merged** defines the status **closed**

:need:`[[title]] <rl__committer>` has the freedom to reject it at any time by setting the status
to "reject".
