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

.. _release_workflows:

Workflow Release Management
###########################

.. workflow:: Create/Maintain Module Release Note
   :id: wf__rel_mod_rel_note
   :status: valid
   :responsible: rl__committer
   :approved_by: rl__project_lead
   :input: wp__module_safety_package, wp__module_sw_release_plan, wp__verification_module_ver_report
   :output: wp__module_sw_release_note
   :contains: gd_temp__rel_mod_rel_note, gd_guidl__rel_management
   :has: doc_concept__rel_process, doc_getstrt__release_process

   The module release note is created for each release by the committer acting as the module lead.
   It may be updated later in case of bugs are found after the release is published.

.. workflow:: Create/Maintain Platform Release Note
   :id: wf__rel_platform_rel_note
   :status: valid
   :responsible: rl__project_lead
   :approved_by: rl__project_lead
   :input: wp__platform_safety_package, wp__platform_sw_release_plan, wp__verification_platform_ver_report
   :output: wp__platform_sw_release_note
   :contains: gd_temp__rel_plat_rel_note, gd_guidl__rel_management
   :has: doc_concept__rel_process, doc_getstrt__release_process

   The platform release note is prepared and approved by the project lead circle.
   It may be updated later in case of bugs found after the release is published.

.. workflow:: Plan Module Release
   :id: wf__rel_mod_rel_plan
   :status: valid
   :responsible: rl__committer
   :approved_by: rl__project_lead
   :input: wp__issue_track_system, wp__platform_mgmt
   :output: wp__module_sw_release_plan
   :contains: gd_temp__rel_issue, gd_guidl__rel_management
   :has: doc_concept__rel_process, doc_getstrt__release_process

   The module release plan is created as part of the modules planning and documented as part of the module's project planning.

.. workflow:: Plan Platform Release
   :id: wf__rel_plat_rel_plan
   :status: valid
   :responsible: rl__project_lead
   :approved_by: rl__project_lead
   :input: wp__issue_track_system, wp__platform_mgmt
   :output: wp__platform_sw_release_plan
   :contains: gd_temp__rel_issue, gd_guidl__rel_management
   :has: doc_concept__rel_process, doc_getstrt__release_process

   The platform release plan is created as part of the project planning and documented in the platform management plan.

RAS(IC) for Release Management:
*******************************

.. needtable:: RASIC Overview for Release Management
   :tags: release_mgt
   :filter: "release_mgt" in tags and type == "workflow" and is_external == False
   :style: table
   :sort: status
   :columns: id as "Activity";responsible as "Responsible";approved_by as "Approver";supported_by as "Supporter"
   :colwidths: 30,30,30,30
