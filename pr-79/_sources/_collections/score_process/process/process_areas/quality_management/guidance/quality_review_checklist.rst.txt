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

.. _quality workproduct review checklist:

Checklist Quality Work Product Review
=====================================

.. gd_chklst:: Quality Work Product Review Checklist
   :id: gd_chklst__review_checklist
   :status: valid
   :tags: quality_management


.. note:: A lot of formal checks, defined in the process requirements, are implemented in the CI pipeline. So it's checked for example that all needed attributes of a document are filled out.
          Additional checks are needed and focussed on the content of the work products. Therefore the provided checklists can be used.

General plan review checklist template
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table:: General plan review checklist template
        :header-rows: 1
        :widths: 10,30,10,30,20

        * - Review Id
          - Acceptance criteria
          - passed [yes | no]
          - Remarks
          - Issue link
        * - PMP_00_00
          - Are the provided templates are used?
          -
          - Check folder templates / process description for available templates. Deviations need to have an approved argumentation by the CODEOWNER.
          -
        * - PMP_00_01
          - Is the document up to date?
          -
          - Check with author if the document is still up to date. Consult also Github Issues for planned updates.
          -
        * - PMP_00_02
          - If there were changes related to the last release is there are related planning available?
          -
          - Look for related issues (improvement, bugfix, task) in the issue tracking system.
          -
        * - PMP_00_03
          - Is the status of the issues according to the document?
          -
          - Look in the status and also the history of the related issues.
          -
        * - PMP_00_04
          - Are there any open issues related to the last release?
          -
          - Look description of last release.
          -
        * - PMP_00_05
          - Are all documents have the status "valid"?
          -
          - Needed for every release.
          -

Project Management plan review checklist template
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table:: Project Management plan review checklist template
        :header-rows: 1
        :widths: 10,30,10,30,20

        * - Review Id
          - Acceptance criteria
          - passed [yes | no]
          - Remarks
          - Issue link
        * - PJP_00_01
          - Are the purpose and goals of the project defined (including references to related projects, if existing)?
          -
          - The purpose and goals should be clearly stated.
          -
        * - PJP_00_02
          - Is the scope of the project defined?
          -
          - Also highly recommended is to define what is out of scope.
          -
        * - PJP_00_04
          - Is the project life-cycle defined?
          -
          - The project life-cycle shall match to the purpose and goals of the project.
          -
        * - PJP_00_05
          - Are major project metrics to track the progress described?
          -
          - Metrics shall be consistent to quality report.
          -
        * - PJP_01_01
          - Are all for the project necessary roles assigned to team members?
          -
          - Check issue tracking system for assigned roles. Are there any issues that are not assigned? Are the assigned
            issues assigned to the right persons?
          -
        * - PJP_01_02
          - Are skill needs and planned trainings documented/referenced?
          -
          - Check training plan and issue tracking system for related issues.
          -
        * - PJP_02_01
          - Are the project milestones described/referenced? (And are they feasible?)
          -
          - Look on the planning boards in the issue tracking system.
          -
        * - PJP_02_02
          - Are project activities defined, assigned and scheduled according to the defined project life cycle and estimations in a work breakdown structure?
          -
          - Check if activities matching to the project life cycle.
          -
        * - PJP_02_03
          - Are project activities monitored and adjusted?
          -
          - Check if the status of the activities are up to date.
          -
        * - PJP_02_04
          - Are the activities structured and of a manageable size?
          -
          - The project plans shall be structured as described in the project management plan.
          -
        * - PJP_02_05
          - Is the technical infrastructure and resources needed described?
          -
          - Check if technical infrastructure and resources match to the project needs.
          -
        * - PJP_03_01
          - Are communication interfaces between all involved parties defined (who communicates, what, in which intervals, over which channels, internal vs. Customer communication)?
          -
          - Check if communication interfaces are defined and followed.
          -
        * - PJP_04_01
          - Have the reports for the project being defined? (Including required content, maintenance schedule etc.).
          -
          - Check if reports are defined and available.
          -


Safety Management plan review checklist templates
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table:: Safety Management plan review checklist template
        :header-rows: 1
        :widths: 10,90

        * - Review Id
          - Link to checklist
        * - SafMP_00_01
          - :need:`gd_chklst__safety_plan`


Security Management plan review checklist template
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table:: Security Management plan review checklist template
        :header-rows: 1
        :widths: 10,90

        * - Review Id
          - Link to checklist
        * - SecMP_00_01
          - :need:`gd_chklst__security_plan`


Quality Management plan review checklist template
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table:: Quality Management plan review checklist template
        :header-rows: 1
        :widths: 10,30,10,30,20

        * - Review Id
          - Acceptance criteria
          - passed [yes | no]
          - Remarks
          - Issue link
        * - QMP_00_01
          - Are the scope and goals defined (including references to related quality standards, internal regulations etc. if existing)?
          -
          - Are the quality objectives and scope aligned with the project’s standards and stakeholder requirements?
          -
        * - QMP_00_02
          - Are work product quality goals defined?
          -
          - Check the definition and also if they are reachable.
          -
        * - QMP_00_03
          - Are roles and responsibilities in the process area of quality management defined?
          -
          - Check if all needed roles are assigned to team members.
          -
        * - QMP_01_01
          - Are quality goals and metrics for in the project specified, tracked and are they suitable for process improvement?
          -
          - Check if the defined metrics are measurable and suitable for process improvement. Check if there is a tracking done in the issue tracking system.
          -
        * - QMP_01_02
          - Do all quality metrics have an acceptance criteria specified?
          -
          - Check if acceptance criteria are defined for all quality metrics.
          -
        * - QMP_01_03
          - Is quality reporting described including cadence, relevant parties and documentation?
          -
          - Check if the quality reporting is following the defined cadence and if all relevant parties are involved.
          -
        * - QMP_02_01
          - Are the quality milestones described or referenced in a quality Schedule, and are they feasible?
          -
          - Check the planning boards in the issue tracking system.
          -
        * - QMP_03_01
          - Is the approach of conducting work product reviews defined and appropriate?
          -
          - Check if the work product reviews are following the defined process and if all relevant parties are involved.
          -
        * - QMP_03_02
          - Is the approach of conducting process audits defined and appropriate?
          -
          - Check if the process audits are following the defined process and if all relevant parties are involved.
          -
        * - QMP_04_01
          - Is the process of handling problems and/or non-conformances defined?
          -
          - Check if there is a defined process for handling problems and non-conformances. Check if there are related issues in the issue tracking system.
          -
        * - QMP_04_02
          - Is there a specification on how to ensure the resolution of process non-conformances?
          -
          - Check if there are defined actions for resolving non-conformances and if they are tracked in the issue tracking system.
          -
        * - QMP_04_03
          - Is there a specification on how to escalate process non-conformances in situations where goals of quality management conflict with those of other process areas?
          -
          - Check if there is a defined escalation process for non-conformances.
          -
        * - QMP_04_04
          - Do the described mechanisms show that quality assurance has the independence and authority to escalate problems to appropriate levels of management?
          -
          - Check if the quality assurance has the independence and authority to escalate problems. This should be ensured by the project set up.
          -
        * - QMP_05_01
          - Are process improvement activities planned, monitored, and documented?
          -
          - Check if there are planned process improvement activities and if they are tracked in the issue tracking system. Check if they are up to date and planned in a realistic way.
          -


Configuration Management plan review checklist template
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table:: Configuration Management plan review checklist template
        :header-rows: 1
        :widths: 10,30,10,30,20

        * - Review Id
          - Acceptance criteria
          - passed [yes | no]
          - Remarks
          - Issue link
        * - CMP_00_01
          - Are the objectives and scope defined?
          -
          - Check if the objectives and scope are clearly defined and understood by all relevant parties.
          -
        * - CMP_00_02
          - Is the project lifecycle according to the configuration management plan?
          -
          - Check if the project lifecycle is followed as defined in the configuration management plan.
          -
        * - CMP_00_03
          - Are retrievals(s) described?
          -
          - Check if the retrieval processes are clearly described and followed.
          -
        * - CMP_00_04
          - Are the branches and baselines described?
          -
          - Check if the branching and baseline strategies are clearly defined and followed.
          -
        * - CMP_00_05
          - Is the backup and recovery for the project described?
          -
          - Check if the backup and recovery procedures are clearly described and followed.
          -
        * - CMP_00_06
          - Is the configuration management tooling (inclusive tool names and CI build tools) described?
          -
          - Check if the configuration management tools are clearly described and used as defined.
          -


Tool Management plan review checklist template
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table:: Tool Management plan review checklist template
        :header-rows: 1
        :widths: 10,90

        * - Review Id
          - Link to checklist
        * - TMP_00_01
          - :need:`gd_chklst__tool_cr_review`


Release Management plan review checklist template
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table:: Release Management plan review checklist template
        :header-rows: 1
        :widths: 10,30,10,30,20

        * - Review Id
          - Acceptance criteria
          - passed [yes | no]
          - Remarks
          - Issue link
        * - RMP_00_01
          - Are release notes available for every release?
          -
          - Check if release notes are created for every release. Check if the template is used and the content is complete.
          -


Problem Resolution plan review checklist template
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table:: Problem Resolution plan review checklist template
        :header-rows: 1
        :widths: 10,90

        * - Review Id
          - Link to checklist
        * - PMMP_00_01
          - :need:`gd_chklst__problem_cr_review`


Change Management plan review checklist template
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table:: Change Management plan review checklist template
        :header-rows: 1
        :widths: 10,90

        * - Review Id
          - Link to checklist
        * - ChMP_00_01
          - :need:`gd_chklst__change_cr_review`


Software Verification plan review checklist template
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table:: Software verification review checklist template
        :header-rows: 1
        :widths: 10,30,10,30,20

        * - Review Id
          - Acceptance criteria
          - passed [yes | no]
          - Remarks
          - Issue link
        * - SWV_00_01
          - Are the objectives and scope defined?
          -
          - Check if the objectives and scope are clearly defined and understood by all relevant parties.
          -
        * - SWV_00_02
          - Are the verification methods documented and up to date?
          -
          - Check if the verification methods are clearly described and followed.
          -
        * - SWV_00_03
          - Are the test derivation methods documented and up to date?
          -
          - Check if the test derivation methods are clearly described and followed.
          -
        * - SWV_00_04
          - Are the software quality criteria defined and documented?
          -
          - Check if the software quality criteria are clearly defined and understood by all relevant parties. Have a look on the reports to verify if the criteria are fulfilled.
          -
        * - SWV_00_05
          - Are all used tools described?
          -
          - Check if all tools used for software verification are clearly described and used as defined. Are additional tools used that are not described?
          -
        * - SWV_00_06
          - Are verification setups and variants described, documented and up to date?
          -
          - Check if the verification setups and variants are clearly described and followed.
          -


Documentation Management plan review checklist template
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table:: Documentation Management plan review checklist template
        :header-rows: 1
        :widths: 10,90

        * - Review Id
          - Link to checklist
        * - DMP_00_01
          - :need:`gd_chklst__documentation_review`


Software Development Plan review checklist template
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table:: Software Development Plan review checklist template
        :header-rows: 1
        :widths: 10,30,10,30,20

        * - Review Id
          - Acceptance criteria
          - passed [yes | no]
          - Remarks
          - Issue link
        * - SDP_00_01
          - Are the objectives and scope defined?
          -
          - Check if the objectives and scope are clearly defined and understood by all relevant parties.
          -
        * - SDP_00_02
          - Are the design and programming languages defined?
          -
          - Check if the design and programming languages are clearly defined and suitable for the project.
          -
        * - SDP_00_03
          - Are coding guidelines available, documented and up to date?
          -
          - Check if coding guidelines are followed and if they are up to date.
          -
        * - SDP_00_04
          - Is a software configuration guideline available, documented and up to date?
          -
          - Check if the software configuration guideline is followed and if deviations have an approved argumentation by the CODEOWNER.
          -
        * - SDP_00_05
          - Are all SW development tools described?
          -
          - Check if all tools used for software development are clearly described. If possible check if they are used as defined.
          -
