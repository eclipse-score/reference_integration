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

.. _quality_workflows:

Workflows
---------

.. workflow:: Create/Maintain Quality Management Plan
   :id: wf__cr_mt_qlm_plan
   :status: valid
   :responsible: rl__quality_manager
   :approved_by: rl__project_lead
   :supported_by:
   :input: wp__policies, wp__issue_track_system, wp__platform_mgmt
   :output: wp__qms_plan
   :contains: gd_guidl__qlm_plan_definitions, gd_temp__qlm_plan
   :has: doc_concept__quality_process, doc_getstrt__quality_process

   | The Quality Management Plan is created and maintained by the :need:`rl__quality_manager`.

.. workflow:: Verify/Approve Platform Release
   :id: wf__vy_ap_pltrelease
   :status: valid
   :responsible: rl__quality_manager
   :approved_by: rl__project_lead
   :input: wp__qms_plan
   :output: wp__platform_sw_release_note
   :contains: gd_guidl__qlm_plan_definitions, gd_chklst__review_checklist
   :has: doc_concept__quality_process, doc_getstrt__quality_process

   | The project/platform release is verified and approved.

.. workflow:: Execute Platform Process Audit
   :id: wf__exe_pltprocess_audit
   :status: valid
   :responsible: rl__quality_manager
   :approved_by: rl__project_lead
   :supported_by: rl__safety_manager, rl__security_manager
   :input: wp__qms_plan, wp__process_description
   :output: wp__process_impr_report
   :contains: gd_guidl__qlm_plan_definitions, gd_chklst__review_checklist
   :has: doc_concept__quality_process, doc_getstrt__quality_process

   | The project/platform processes are audited.

.. workflow:: Execute Feature Contribution Conformance Checks
   :id: wf__exe_featprocess_conformance_checks
   :status: valid
   :responsible: rl__quality_manager
   :approved_by: rl__project_lead
   :supported_by: rl__safety_manager, rl__security_manager
   :input: wp__qms_plan, wp__feat_request, wp__process_description
   :output: wp__qms_report
   :contains: gd_guidl__qlm_plan_definitions, gd_chklst__review_checklist
   :has: doc_concept__quality_process, doc_getstrt__quality_process

   | The conformance of the feature contribution is checked. The conformance check consists of
   | * No open issues that are related to quality that are relevant for the feature contribution
   | * All required work products are provided and fulfill the quality criteria as defined in :need:`wp__qms_plan`
   | * Work product reviews are performed and passed for all required work products as defined in :need:`wp__qms_plan`
   | * Quality management plan is up to date and reflects the current state of the :need:`wp__platform_mgmt`

.. workflow:: Execute Work Product Reviews
   :id: wf__exe_wp_review
   :status: valid
   :responsible: rl__quality_manager
   :approved_by: rl__project_lead
   :supported_by: rl__committer
   :input: wp__qms_plan, wp__process_description
   :output: wp__verification_platform_ver_report
   :contains: gd_guidl__qlm_plan_definitions, gd_chklst__review_checklist, gd_guidl__wp_review
   :has: doc_concept__quality_process, doc_getstrt__quality_process

   | The quality of the work products is assured.

.. workflow:: Consult and Execute Quality Trainings
   :id: wf__consult_exe_qly_training
   :status: valid
   :responsible: rl__quality_manager
   :approved_by: rl__project_lead
   :supported_by: rl__safety_manager, rl__security_manager
   :input: wp__qms_plan, wp__policies, wp__process_description
   :output: wp__training_path
   :contains: gd_guidl__qlm_plan_definitions
   :has: doc_concept__quality_process, doc_getstrt__quality_process

   | The :need:`rl__quality_manager` consults all project/platform stakeholder as defined in :need:`doc_concept__quality_process` for quality topics and executes regularly quality trainings.

.. workflow:: Monitor/Improve Quality Activities
   :id: wf__mr_imp_qlm_plan_processes
   :status: valid
   :responsible: rl__quality_manager
   :approved_by: rl__project_lead
   :supported_by: rl__safety_manager, rl__security_manager
   :input: wp__qms_plan, wp__platform_sw_release_note, wp__module_sw_release_note, wp__process_impr_report, wp__qms_report, wp__verification_platform_ver_report, wp__verification_module_ver_report, wp__training_path
   :output: wp__issue_track_system
   :contains: gd_guidl__qlm_plan_definitions, gd_chklst__review_checklist, gd_req__quality_report
   :has: doc_concept__quality_process, doc_getstrt__quality_process

   | The :need:`rl__quality_manager` is responsible for the monitoring of the activities against the quality management plan.
   | The :need:`rl__quality_manager` is responsible to adjust the quality management plan, if deviations are detected.


.. needextend:: "process_areas/quality_management" in docname
   :+tags: quality_management

RAS(IC) for Safety Analysis
***************************

.. needtable:: RASIC Overview for Quality Management
   :tags: quality_management
   :filter: "quality_management" in tags and type == "workflow"
   :style: table
   :sort: status
   :columns: id as "Activity";responsible as "Responsible";approved_by as "Approver";supported_by as "Supporter"
   :colwidths: 30,30,30,30
