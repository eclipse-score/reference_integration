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

.. _workflow_safety_management:

Safety Management Workflows
###########################

.. workflow:: Create/Maintain Safety Plan
   :id: wf__cr_mt_safety_plan
   :status: valid
   :responsible: rl__safety_manager
   :approved_by: rl__project_lead
   :input: wp__platform_mgmt, wp__issue_track_system, wp__sw_component_class, wp__tailoring
   :output: wp__module_safety_plan, wp__platform_safety_plan
   :contains: gd_guidl__saf_plan_definitions, gd_temp__feature_safety_wp, gd_temp__module_safety_plan
   :has: doc_concept__safety_management_process, doc_getstrt__safety_management_process

   | The Safety Manager is responsible for the planning and coordination of the safety activities for the platform.
   | The Safety Manager creates and maintains the safety plan.
   | For this a template exists to guide the creator of the safety plan.

.. workflow:: Create Component Classification
   :id: wf__cr_comp_class
   :status: valid
   :responsible: rl__committer
   :approved_by: rl__safety_manager
   :input: wp__platform_mgmt, wp__issue_track_system
   :output: wp__sw_component_class
   :contains: gd_guidl__component_classification, gd_temp__component_classification
   :has: doc_concept__safety_management_process, doc_getstrt__safety_management_process

   | The Safety Manager shall approve the OSS component classification performed by an expert on this component.

.. workflow:: Create/Maintain Safety Package
   :id: wf__cr_mt_safety_package
   :status: valid
   :responsible: rl__safety_engineer
   :approved_by: rl__safety_manager
   :input: wp__module_safety_plan, wp__platform_safety_plan, wp__issue_track_system
   :output: wp__module_safety_package, wp__platform_safety_package
   :contains: gd_guidl__saf_package, gd_temp__feature_safety_wp, gd_temp__module_safety_plan
   :has: doc_concept__safety_management_process, doc_getstrt__safety_management_process

   | The Safety Manager in the project is NOT responsible to provide the argument for the achievement of functional safety.
   | But the Safety Manager creates and maintains the safety package in the sense of a collection of safety related work products.
   | The generation and the maintenance of this draft safety package shall be automated as much as possible.
   | It does not contain the final argumentation of the safety of the product.
   | As the safety package is only a collection of work products, the safety plan (template) can be used for documentation.

.. workflow:: Perform Safety Audit
   :id: wf__p_fs_audit
   :status: valid
   :responsible: rl__external_auditor
   :approved_by: rl__safety_manager
   :input: wp__module_safety_plan, wp__platform_safety_plan, wp__module_safety_package, wp__platform_safety_package
   :output: wp__audit_report
   :contains: gd_guidl__saf_plan_definitions
   :has: doc_concept__safety_management_process, doc_getstrt__safety_management_process

   | The external auditor is responsible to perform a safety audit.
   | The Safety Manager and the process community shall support the external auditor during this.
   | The Project Manager and and the Safety Manager shall approve the audit report.

.. workflow:: Perform Formal Reviews
   :id: wf__p_formal_rv
   :status: valid
   :responsible: rl__external_auditor
   :approved_by: rl__safety_manager
   :input: wp__module_safety_plan, wp__platform_safety_plan, wp__module_safety_package, wp__platform_safety_package
   :output: wp__fdr_reports
   :contains: gd_guidl__saf_plan_definitions, gd_chklst__safety_plan, gd_chklst__safety_package
   :has: doc_concept__safety_management_process, doc_getstrt__safety_management_process

   | The external auditor is responsible to perform the formal reviews on safety plan, safety package and safety analysis.
   | The Safety Manager shall support the external auditor during the reviews.
   | The Project Manager and and the Safety Manager shall approve the formal reviews.
   | Therefore a checklists exist to guide the creator of the relevant safety documents.

.. workflow:: Create/Maintain Safety Manual
   :id: wf__cr_mt_safety_manual
   :status: valid
   :responsible: rl__safety_engineer
   :approved_by: rl__safety_manager
   :input: wp__requirements_feat_aou, wp__requirements_feat, wp__feature_arch, wp__feature_fmea, wp__feature_dfa, wp__requirements_comp_aou, wp__requirements_comp, wp__component_arch, wp__sw_component_fmea, wp__sw_component_dfa
   :output: wp__platform_safety_manual, wp__module_safety_manual
   :contains: gd_guidl__saf_man, gd_temp__safety_manual
   :has: doc_concept__safety_management_process, doc_getstrt__safety_management_process

   | The Safety Engineer collects the necessary input for the safety manuals on platform and module level and documents it.
   | The safety manager makes sure all items are in valid state for a release of the safety manual.
   | Also for the safety manual a template exists as a guidance.

.. workflow:: Monitor/Verify Safety
   :id: wf__mr_vy_safety
   :status: valid
   :responsible: rl__safety_manager
   :approved_by: rl__project_lead
   :input: wp__module_safety_plan, wp__platform_safety_plan, wp__module_safety_package, wp__platform_safety_package, wp__audit_report, wp__fdr_reports
   :output: wp__issue_track_system, wp__module_sw_release_note, wp__platform_sw_release_note
   :contains: gd_guidl__saf_plan_definitions
   :has: doc_concept__safety_management_process, doc_getstrt__safety_management_process

   | The Safety Manager is responsible for the monitoring of the safety activities against the safety plan.
   | The Safety Manager is responsible to verify, that the preconditions for the release, which are  part of the release notes, are fulfilled.
   | The Safety Manager is responsible to verify the correctness, completeness and consistency of the release notes.

.. workflow:: Impact Analysis of Change Request
   :id: wf__impact_analysis_change_request
   :status: valid
   :responsible: rl__safety_manager
   :approved_by: rl__project_lead
   :input: wp__platform_mgmt, wp__issue_track_system, wp__sw_component_class, wp__tailoring
   :output: wp__issue_track_system
   :contains: gd_temp__change_component_request, gd_temp__change_decision_record, gd_temp__change_impact_analysis
   :has: doc_concept__safety_management_process

   | In accordance with ISO 26262-2:2018 section 5.2.2.3 d/e (Impact Analysis), the project implements a dedicated workflow for analyzing change requests.
   | The Safety Manager is responsible for ensuring that each change request is analyzed for its impact on safety, as required by ISO 26262-2:2018.
   | Impact analysis is performed at the element level (e.g., module or component) rather than the item (system) level, reflecting the modular architecture of the platform. This tailoring is documented in the safety plan and justified by the project structure and scope.
   | The analysis includes:
   |   - Reviewing the change request and its context
   |   - Assessing the impact on affected elements, safety requirements, and work products
   |   - Documenting the rationale for decisions regarding acceptance, implementation, or rejection of the change
   | The outcome is a change impact analysis report and a documented decision, which are reviewed and approved as part of the Safety Management process.
