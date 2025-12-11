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

.. _chm_change_workflows:

Workflow Change Management
##########################

.. workflow:: Create Change Request
   :id: wf__change_create_cr
   :status: valid
   :tags: change_management
   :responsible: rl__contributor
   :approved_by: rl__committer
   :supported_by: rl__project_lead, rl__safety_manager, rl__security_manager, rl__quality_manager
   :input: wp__policies, wp__issue_track_system, wp__feat_request, wp__cmpt_request
   :output: wp__issue_track_system, wp__feat_request, wp__cmpt_request
   :contains: gd_guidl__change_change_request, gd_temp__change_feature_request, gd_temp__change_component_request, gd_temp__change_impact_analysis, gd_temp__component_classification, gd_temp__change_decision_record
   :has: doc_concept__change_process, doc_getstrt__change_process

   The Change Request is created.

   For creating the Change Request template must be used. Check here for the available
   templates: :need:`doc_getstrt__change_process` or :need:`gd_guidl__change_change_request`.

   To start the analysis the Change Request status is changed to "in review"

.. workflow:: Analyze Change Request
   :id: wf__change_analyze_cr
   :status: valid
   :tags: change_management
   :responsible: rl__contributor
   :approved_by: rl__project_lead
   :supported_by: rl__committer, rl__safety_manager, rl__security_manager, rl__quality_manager
   :input: wp__policies, wp__issue_track_system, wp__feat_request, wp__cmpt_request
   :output: wp__issue_track_system, wp__feat_request, wp__cmpt_request
   :contains: gd_guidl__change_change_request, gd_temp__change_feature_request, gd_temp__change_component_request, gd_temp__change_impact_analysis, gd_temp__component_classification, gd_temp__change_decision_record
   :has: doc_concept__change_process, doc_getstrt__change_process

   The Change Request is analyzed.

   Until the template is not filled out properly, the Change Request may be set back to
   “open” from the :need:`Committer <rl__committer>`.

   If the Change Request shall be implemented, the Change Request status is set to
   "in implementation", otherwise to "rejected".

   The author of the Change Request may cancel it, thus the status is set to "rejected".

.. workflow:: Implement and Monitor Change Request
   :id: wf__change_implement_monitor_cr
   :status: valid
   :tags: change_management
   :responsible: rl__contributor
   :approved_by:  rl__committer
   :supported_by: rl__project_lead, rl__safety_manager, rl__security_manager, rl__quality_manager
   :input: wp__issue_track_system, wp__feat_request, wp__cmpt_request
   :output: wp__issue_track_system, wp__feat_request, wp__cmpt_request
   :contains: gd_guidl__change_change_request, gd_temp__change_feature_request, gd_temp__change_component_request, gd_temp__change_impact_analysis, gd_temp__component_classification, gd_temp__change_decision_record
   :has: doc_concept__change_process, doc_getstrt__change_process

   The Change Request is implemented and monitored.

   This may require additional activities, including creating ISSUEs and PRs.
   These are linked to the Change Request and monitored until closure.

   The Change Request is done, if all linked activities has been closed and confirmed.
   Before closing the Change Request, :need:`Committer <rl__committer>` must check the
   correctness.

   The :need:`Committer <rl__committer>` may still reject it, thus the status is set to
   "rejected".

   The author of the Change Request may cancel it, thus the status is set to "rejected".

.. workflow:: Close Change Request
   :id: wf__change_close_cr
   :status: valid
   :tags: change_management
   :responsible: rl__committer
   :approved_by: rl__project_lead
   :supported_by: rl__safety_manager, rl__security_manager, rl__quality_manager
   :input: wp__issue_track_system, wp__feat_request, wp__cmpt_request
   :output: wp__issue_track_system, wp__feat_request, wp__cmpt_request
   :contains: gd_guidl__change_change_request, gd_temp__change_feature_request, gd_temp__change_component_request, gd_temp__change_impact_analysis, gd_temp__component_classification, gd_temp__change_decision_record
   :has: doc_concept__change_process, doc_getstrt__change_process

   The Change Request is closed.

   The Change Request is closed only, if the implementation is sufficient. That is verified
   by the :need:`Committer <rl__committer>` finally.

   Otherwise the :need:`Committer <rl__committer>` keeps the status "in implementation".

.. needextend:: docname is not None and "process_areas/change_management" in docname
   :+tags: change_management

RAS(IC) for Change Management:
******************************

.. needtable:: RASIC Overview for Change Management
   :tags: change_management
   :filter: "change_management" in tags and type == "workflow" and is_external == False
   :style: table
   :sort: status
   :columns: id as "Activity";responsible as "Responsible";approved_by as "Approver";supported_by as "Supporter"
   :colwidths: 30,30,30,30
