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

Workflow Implementation
#######################

.. workflow:: Create/Maintain Software Development Plan
   :id: wf__sw_development_plan
   :status: valid
   :tags: implementation
   :responsible: rl__committer
   :approved_by: rl__project_lead
   :input: wp__platform_mgmt
   :output: wp__sw_development_plan
   :contains: gd_temp__software_development_plan
   :has: doc_concept__imp_concept, doc_getstrt__imp_getstrt

   The Software Development Plan shall descirbe
     - methods
     - Guidelines
     - development environment

.. workflow:: Create/Maintain Implementation
   :id: wf__sw_detailed_design
   :status: valid
   :tags: implementation
   :responsible: rl__contributor
   :approved_by: rl__committer
   :input: wp__requirements_comp, wp__component_arch, wp__sw_development_plan
   :output: wp__sw_implementation
   :contains: gd_temp__detailed_design
   :has: doc_concept__imp_concept, doc_getstrt__imp_getstrt

   The implementation is created, consisting of
     - Detailed Design
     - Source Code

.. workflow:: Verify Implementation
   :id: wf__sw_verify_implementation
   :status: valid
   :tags: implementation
   :responsible: rl__committer
   :approved_by: rl__committer
   :input: wp__sw_implementation, wp__sw_development_plan
   :output: wp__issue_track_system, wp__sw_implementation_inspection, wp__verification_module_ver_report
   :contains: gd_chklst__impl_inspection_checklist
   :has: doc_concept__imp_concept, doc_getstrt__imp_getstrt

   The Implementation Verification of the Detailed Design and Code consists of the following topics
     - Detailed Design and Code Inspection
     - Static and Dynamic Code Analysis performed by a tool
