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

.. _process_management_workflows:

Process Management Workflows
############################

For a detailed explanation of workflows and their role within the process model, please refer to the :ref:`processes_introduction`.

.. workflow:: Create/Maintain Process Management Strategy
   :id: wf__cr_mt_process_mgt_strategy
   :status: valid
   :responsible: rl__contributor
   :approved_by: rl__process_community
   :supported_by: rl__external_auditor, rl__project_lead
   :input: wp__policies, wp__issue_track_system
   :output: wp__process_strategy
   :contains: gd_guidl__process_management, gd_temp__process_workflow
   :has: doc_concept__process_management, doc_getstrt__process_management

   The process management strategy is created and maintained.

.. workflow:: Define/Approve Process Description
   :id: wf__def_app_process_description
   :status: valid
   :responsible: rl__contributor
   :approved_by: rl__process_community
   :supported_by: rl__external_auditor, rl__project_lead
   :input: wp__process_strategy, wp__issue_track_system
   :output: wp__process_description
   :contains: gd_guidl__process_management, gd_temp__process_workflow
   :has: doc_concept__process_management, doc_getstrt__process_management

   The process description is defined and approved.

.. workflow:: Monitor/Improve Process Implementation
   :id: wf__mon_imp_process_description
   :status: valid
   :responsible: rl__contributor
   :approved_by: rl__process_community
   :supported_by: rl__external_auditor, rl__project_lead
   :input: wp__process_description
   :output: wp__process_impr_report, wp__issue_track_system
   :contains: gd_guidl__process_management, gd_temp__process_workflow
   :has: doc_concept__process_management, doc_getstrt__process_management

   The process strategy and description implementation is monitored and improvements are
   triggered, if required.


.. needextend:: docname is not None and "process_areas/process_management" in docname
   :+tags: process_management

RAS(IC) for Process Management:
*******************************

.. needtable:: RASIC Overview for Process Management
   :tags: process_management
   :filter: "process_management" in tags and type == "workflow" and is_external == False
   :style: table
   :sort: status
   :columns: id as "Activity";responsible as "Responsible";approved_by as "Approver";supported_by as "Supporter"
   :colwidths: 30,30,30,30
