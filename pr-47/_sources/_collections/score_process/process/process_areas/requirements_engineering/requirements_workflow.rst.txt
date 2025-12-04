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


Workflow Requirements Engineering
#################################

.. workflow:: Create/Maintain Stakeholder requirements and SW-Platform AoU
   :id: wf__req_stkh_req
   :status: valid
   :tags: requirements_engineering
   :responsible: rl__contributor
   :approved_by: rl__technical_lead
   :supported_by: rl__safety_manager
   :input: wp__policies, wp__issue_track_system
   :output: wp__requirements_stkh, wp__requirements_sw_platform_aou
   :contains: gd_temp__req_stkh_req, gd_temp__req_formulation
   :has: doc_concept__req_process, doc_getstrt__req_process

   Stakeholder requirements and SW-Platform Assumptions of Use (AoU) can be created during a change request.
   Any contributor can create a stakeholder requirement (or AoU) and propose it for approval.

.. workflow:: Create/Maintain Feature requirements
   :id: wf__req_feat_req
   :status: valid
   :tags: requirements_engineering
   :responsible: rl__contributor
   :approved_by: rl__technical_lead
   :supported_by: rl__safety_manager, rl__security_manager
   :input: wp__requirements_stkh, wp__issue_track_system
   :output: wp__requirements_feat
   :contains: gd_temp__req_feat_req, gd_temp__req_formulation
   :has: doc_concept__req_process, doc_getstrt__req_process

   Depending on the stakeholder requirements feature requirements can be derived. This can be done by any contributor and will be approved by a technical lead. If needed safety and security managers can provide support.

.. workflow:: Create/Maintain Feature AoUs
   :id: wf__req_feat_aou
   :status: valid
   :tags: requirements_engineering
   :responsible: rl__contributor
   :approved_by: rl__technical_lead
   :supported_by: rl__safety_manager, rl__security_manager
   :input: wp__requirements_feat, wp__feature_arch, wp__issue_track_system
   :output: wp__requirements_feat_aou, wp__platform_safety_manual
   :contains: gd_temp__req_aou_req, gd_temp__req_formulation
   :has: doc_concept__req_process, doc_getstrt__req_process

   Based on the safety concept on feature level, feature AoUs can be derived. See also :ref:`aou_workflow`

.. workflow:: Create/Maintain Component requirements
   :id: wf__req_comp_req
   :status: valid
   :tags: requirements_engineering
   :responsible: rl__contributor
   :approved_by: rl__committer
   :supported_by: rl__safety_manager, rl__security_manager
   :input: wp__requirements_feat, wp__issue_track_system
   :output: wp__requirements_comp
   :contains: gd_temp__req_comp_req, gd_temp__req_formulation
   :has: doc_concept__req_process, doc_getstrt__req_process

.. workflow:: Create/Maintain Component AoUs
   :id: wf__req_comp_aou
   :status: valid
   :tags: requirements_engineering
   :responsible: rl__contributor
   :approved_by: rl__committer
   :supported_by: rl__safety_manager, rl__security_manager
   :input: wp__requirements_comp, wp__component_arch, wp__issue_track_system
   :output: wp__requirements_comp_aou, wp__module_safety_manual
   :contains: gd_temp__req_aou_req, gd_temp__req_formulation
   :has: doc_concept__req_process, doc_getstrt__req_process

   Based on the safety concept on component level, component AoUs can be derived. See also :ref:`aou_workflow`

.. workflow:: Create/Maintain Process and Tool Requirements
   :id: wf__req_proc_tool
   :status: valid
   :tags: requirements_engineering
   :responsible: rl__contributor
   :approved_by: rl__committer
   :supported_by: rl__safety_manager, rl__security_manager
   :input: wp__process_description
   :output: wp__requirements_proc_tool
   :contains: gd_temp__req_process_req, gd_temp__req_tool_req, gd_temp__req_formulation
   :has: doc_concept__req_process, doc_getstrt__req_process

   Based on the process descriptions (which comply to standards) and/or stakeholder requirements process and tool requirements are derived.

.. workflow:: Monitor/Verify Requirements
   :id: wf__monitor_verify_requirements
   :status: valid
   :tags: requirements_engineering
   :responsible: rl__committer
   :approved_by: rl__committer
   :supported_by: rl__safety_manager
   :input: wp__requirements_stkh, wp__requirements_feat, wp__requirements_comp, wp__requirements_feat_aou, wp__requirements_comp_aou, wp__platform_safety_manual, wp__module_safety_manual
   :output: wp__issue_track_system, wp__requirements_inspect
   :contains: gd_chklst__req_inspection

   The requirements are monitored and verified. The inspection shall be implemented as integral part of the review in version management tool.
