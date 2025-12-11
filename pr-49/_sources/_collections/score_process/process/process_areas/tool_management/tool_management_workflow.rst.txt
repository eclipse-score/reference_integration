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

.. _tlm_workflows:

Workflow Tool Management
########################

.. workflow:: Create Tool Verification Report
   :id: wf__tool_create_tool_verification_report
   :status: valid
   :responsible: rl__contributor
   :approved_by: rl__committer
   :supported_by: rl__safety_manager, rl__security_manager, rl__infrastructure_tooling_community
   :input: wp__issue_track_system, wp__tlm_plan
   :output: wp__tool_verification_report
   :contains: gd_temp__tool_management_verif_rpt_template, gd_chklst__tool_cr_review
   :has: doc_concept__tool_process, doc_getstrt__tool_process

   The Tool Verification Report is created during identification of a tool in status
   draft.

   For creating the Tool Verification Report the content of the linked template shall
   be used.

.. workflow:: Evaluate Tool and Update Tool Verification Report
   :id: wf__tool_evaluate_tool
   :status: valid
   :responsible: rl__contributor
   :approved_by: rl__committer, rl__safety_manager, rl__security_manager
   :supported_by: rl__infrastructure_tooling_community
   :input: wp__tool_verification_report
   :output: wp__tool_verification_report
   :contains: gd_temp__tool_management_verif_rpt_template, gd_chklst__tool_cr_review
   :has: doc_concept__tool_process, doc_getstrt__tool_process

   Each identified tool is evaluated. During evaluation the Tool Verification Report
   is updated accordingly.
   After successful evaluation the status of the Tool Verification Report
   is set to evaluated.

   The successful evaluation shall contain a statement, if the tool shall be qualified
   or not.

   If tool qualification is not needed, the next step is :need:`wf__tool_approve_tool_verification_report`
   otherwise continue with :need:`wf__tool_qualify_tool`.

.. workflow:: Qualify Tool and Update Tool Verification Report
   :id: wf__tool_qualify_tool
   :status: valid
   :responsible: rl__contributor
   :approved_by: rl__committer, rl__safety_manager, rl__security_manager
   :supported_by: rl__infrastructure_tooling_community
   :input: wp__tool_verification_report
   :output: wp__tool_verification_report
   :contains: gd_temp__tool_management_verif_rpt_template, gd_chklst__tool_cr_review
   :has: doc_concept__tool_process, doc_getstrt__tool_process

   The identified tool is qualified, if applicable. During qualification the Tool
   Verification Report is updated accordingly.
   After successful qualification the status of the Tool Verification Report
   is set to qualified.

.. workflow:: Approve Tool Verification Report
   :id: wf__tool_approve_tool_verification_report
   :status: valid
   :responsible: rl__safety_manager, rl__security_manager
   :approved_by: rl__project_lead
   :supported_by: rl__infrastructure_tooling_community
   :input: wp__tool_verification_report
   :output: wp__tool_verification_report
   :contains: gd_temp__tool_management_verif_rpt_template, gd_chklst__tool_cr_review
   :has: doc_concept__tool_process, doc_getstrt__tool_process

   Finally the Tool Verification Report is verified and approved, and thus the status
   is set to released.

   If the verification is not successful or due to any other reason, e.g. the tool is
   not needed any more as planned, the tool verification may also rejected at this point.

.. needextend:: docname is not None and "process_areas/tool_management" in docname
   :+tags: tool_management

RAS(IC) for Tool Management:
****************************

.. needtable:: RASIC Overview for Tool Management
   :tags: tool_management
   :filter: "tool_management" in tags and type == "workflow" and is_external == False
   :style: table
   :sort: status
   :columns: id as "Activity";responsible as "Responsible";approved_by as "Approver";supported_by as "Supporter"
   :colwidths: 30,30,30,30
